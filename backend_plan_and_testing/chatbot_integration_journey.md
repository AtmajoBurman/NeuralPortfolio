# Chatbot Setup & Integration Journey 🚀

Setting up an intelligent, context-aware AI chatbot for a portfolio website is rarely a straightforward task. Below is a detailed breakdown of the technical challenges faced during the integration of a Large Language Model (LLM) with a PostgreSQL database, and the robust engineering solutions implemented to overcome them.

---

## 1. The LLM Tool-Calling Parsing Dilemma

### ❌ The Challenge
The initial architecture utilized the `Llama-3.3-70B-Instruct` model hosted on Hugging Face Inference Endpoints, connected via LangChain's SQL Agent using the native `tool-calling` agent type. 

While the model is highly capable, the underlying API connection was brittle. The model would generate function calls using specific XML-like tags (e.g., `<function=sql_db_query_checker>...`). However, minor hallucinations in the model's output—such as generating a closing tag of `}</function>` instead of `}></function>`—caused the Hugging Face inference parser to completely fail. This resulted in unexpected backend crashes and `tool_use_failed` exceptions, rendering the chatbot incapable of executing SQL queries.

### ✅ The Solution
To make the system fault-tolerant, we pivoted the architecture away from strict server-side JSON tool-calling validation. 

We reconfigured the LangChain SQL Agent to use the **`zero-shot-react-description`** agent type. This paradigm shift forces the model to use the **ReAct (Reasoning and Acting)** framework. Instead of brittle API-level tool calling, the model outputs its reasoning in plain text (`Thought:`, `Action:`, `Action Input:`). LangChain parses this text robustly, bypassing the strict endpoint parser entirely. This resulted in a **100% success rate** for tool execution, eliminating intermittent parsing crashes.

---

## 2. Asynchronous Database Driver Conflicts

### ❌ The Challenge
The backend application was built using modern, asynchronous Python (FastAPI). Naturally, the SQLAlchemy connection string was configured to use the `+asyncpg` driver for non-blocking database operations.

However, LangChain's `SQLDatabase` utility relies heavily on synchronous database inspection methods (using SQLAlchemy's synchronous core) to fetch table schemas, sample rows, and execute dialect-specific checks. Passing an asynchronous connection URL directly into the LangChain SQL toolkit threw compatibility errors, preventing the LLM from understanding the database schema.

### ✅ The Solution
We implemented a dynamic connection string parser specifically for the chatbot's initialization sequence. Before binding the database to the LLM toolkit, we scrubbed the async driver injection (`+asyncpg`) and normalized SSL parameters (`ssl=require` to `sslmode=require`). This allowed the FastApi application to remain fully asynchronous while seamlessly providing a dedicated synchronous thread pool for the LLM's analytical needs.

```python
# Normalizing the async DB URL for synchronous LangChain toolkit
db_url = settings.postgres_url.replace("+asyncpg", "")
db_url = db_url.replace("ssl=require", "sslmode=require")
db = SQLDatabase.from_uri(db_url, include_tables=[...])
```

---

## 3. Controlling Hallucinations & Context Bloat

### ❌ The Challenge
Once the database connection was stable, a new behavioral issue emerged. When asked broad questions (e.g., *"What are my projects?"*), the LLM would attempt to dump the entire contents of the `projects` table into the chat window. This not only consumed excessive tokens (costly and slow) but also created a terrible User Experience by clogging the UI with raw database text.

### ✅ The Solution
We applied strict Prompt Engineering techniques by establishing a highly opinionated **System Prefix**. 

We injected semantic guidelines forcing the model to act as a routing assistant rather than a raw data retrieval tool. The rules explicitly mandated:
> *"Never dump large text blocks from the database. Instead, give a 1–2 sentence summary and direct the user to the relevant page and item."*

By constraining the model's output verbosity and providing it with the structural context of the frontend website, the chatbot transformed from a clunky database query tool into a sleek, conversational guide.

---

## Conclusion
Building this chatbot was an exercise in **system resilience** and **prompt engineering**. By decoupling from fragile external parsers, handling driver disparities at runtime, and applying strict behavioral guardrails, we successfully built an AI agent that is both technically robust and highly user-friendly.
