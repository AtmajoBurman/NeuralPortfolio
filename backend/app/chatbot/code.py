from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
import os
import logging
from dotenv import load_dotenv
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import re


from app.chatbot.system_prefix import SYSTEM_PREFIX as system_prefix
from app.chatbot.model import HUGGING_FACE_MODEL


def strip_markdown(text):
    # Remove bold/italic markers
    text = re.sub(r'(\*{1,2}|_{1,2})(.*?)\1', r'\2', text)
    # Remove headings (#)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    return text

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

_agent_executor = None

def get_agent_executor():
    global _agent_executor
    if _agent_executor is None:
        try:
            from app.config import settings
            hf_api_ = os.getenv("HUGGINGFACE_API_TOKEN")
            db_url = settings.postgres_url

            # Remove +asyncpg if present because SQLDatabase uses a sync driver
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

            memory = ConversationBufferMemory(
                memory_key="chat_history",      # key must match agent_kwargs input_variables
                return_messages=True
            )

            SYSTEM_PREFIX = system_prefix

            toolkit = SQLDatabaseToolkit(db=db, llm=llm)

            _agent_executor = create_sql_agent(
                llm=llm,
                toolkit=toolkit,
                agent_type="zero-shot-react-description",
                verbose=True,
                prefix=SYSTEM_PREFIX,
                agent_executor_kwargs={
                    "handle_parsing_errors": True,
                    "handle_tool_error": True,
                    "memory": memory
                }
            )
        except Exception as e:
            logger.error(f"Error initializing chatbot agent executor: {e}", exc_info=True)
            raise e
            
    return _agent_executor

def get_chatbot_response(user_input: str) -> str:
    """
    Invokes the chatbot agent with the given user input and returns the generated text response.
    """
    try:
        agent = get_agent_executor()
        response = agent.invoke({"input": user_input})
        return strip_markdown(response.get("output", "No response generated."))
    except Exception as e:
        logger.error(f"Error invoking chatbot agent: {e}", exc_info=True)
        # Handle edge cases and failures gracefully
        return "I'm so sorry, but I'm currently having trouble connecting to my database or processing your request. Please try again later, or reach out to the admin directly via LinkedIn or email!"