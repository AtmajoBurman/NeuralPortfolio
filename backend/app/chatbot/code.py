from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
import os
import logging
from dotenv import load_dotenv
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_core.prompts import PromptTemplate
from langchain_community.agent_toolkits.sql.prompt import SQL_SUFFIX
from langchain_classic.agents.mrkl.prompt import FORMAT_INSTRUCTIONS
import re

from app.chatbot.system_prefix import SYSTEM_PREFIX as system_prefix
from app.chatbot.model import HUGGING_FACE_MODEL


def strip_markdown(text):
    text = re.sub(r'(\*{1,2}|_{1,2})(.*?)\1', r'\2', text)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    return text


logger = logging.getLogger(__name__)
load_dotenv()

_agent_executor = None


def get_agent_executor():
    global _agent_executor
    if _agent_executor is not None:
        return _agent_executor

    try:
        from app.config import settings
        hf_api_ = os.getenv("HUGGINGFACE_API_TOKEN")
        db_url = settings.postgres_url
        db_url = db_url.replace("+asyncpg", "")
        db_url = db_url.replace("ssl=require", "sslmode=require")

        db = SQLDatabase.from_uri(
            db_url,
            include_tables=[
                "student_details",
                "sgpa_tracker",
                "cgpa_tracker",
                "profiles",
                "projects",
                "achievements",
                "chit_chat"
            ]
        )

        llm_endpoint = HuggingFaceEndpoint(
            repo_id=HUGGING_FACE_MODEL,
            huggingfacehub_api_token=hf_api_
        )
        llm = ChatHuggingFace(llm=llm_endpoint)

        toolkit = SQLDatabaseToolkit(db=db, llm=llm)

        # ── Prompt ───────────────────────────────────────────────────────────
        # Build a single clean template.
        # {tools} and {tool_names} are injected by create_sql_agent automatically.
        # Do NOT include SQL_PREFIX here — it duplicates tool instructions and
        # conflicts with your SYSTEM_PREFIX.
        template = """{system_prefix}

You have access to the following tools:
{{tools}}

{format_instructions}

{sql_suffix}""".format(
            system_prefix=system_prefix,
            format_instructions=FORMAT_INSTRUCTIONS,
            sql_suffix=SQL_SUFFIX,
        )

        # create_sql_agent expects these input variables in the prompt
        prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad"],
            template=template + "\n\nQuestion: {{input}}\n{{agent_scratchpad}}"
        )
        prompt = prompt.partial(dialect=toolkit.dialect, top_k="10")

        _agent_executor = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            agent_type="zero-shot-react-description",
            verbose=True,
            prompt=prompt,
            max_iterations=6,
            early_stopping_method="force",          # ✅ "generate" is unsupported
            agent_executor_kwargs={
                "handle_parsing_errors": (
                    "Check your output format. "
                    "Once you have queried the database and received results, "
                    "stop immediately and write: Final Answer: <your answer>. "
                    "Do NOT query again."
                ),
                "handle_tool_error": True,
                # ✅ Memory removed — ConversationBufferMemory is deprecated and
                # wasn't wiring correctly anyway. Portfolio Q&A is stateless by nature.
                # If you need memory later, use LangGraph with MemorySaver instead.
            }
        )

    except Exception as e:
        logger.error(f"Error initializing chatbot agent executor: {e}", exc_info=True)
        raise e

    return _agent_executor


def get_chatbot_response(user_input: str) -> str:
    try:
        agent = get_agent_executor()
        response = agent.invoke({"input": user_input})
        return strip_markdown(response.get("output", "No response generated."))
    except Exception as e:
        logger.error(f"Error invoking chatbot agent: {e}", exc_info=True)
        return (
            "I'm so sorry, but I'm currently having trouble connecting to my database "
            "or processing your request. Please try again later, or reach out to the "
            "admin directly via LinkedIn or email!"
        )