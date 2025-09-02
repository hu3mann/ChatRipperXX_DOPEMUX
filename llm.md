llm.md — Model Configuration & Usage
Status: Draft | Owner: <TBD> | Last Updated: 2025‑09‑02
Available Models
Model	Description	Recommended Use
Gemma (9B) via Ollama	Local model running on your machine; deterministic and cost‑free.	Use for day‑to‑day coding, refactoring and test writing.
Claude Sonnet 4	Cloud model with larger context windows and higher accuracy.	Use when Gemma’s confidence is low or when tasks span multiple files.
Claude Opus 4	Premium cloud model with advanced reasoning capabilities.	Use for complex algorithm design, architecture decisions and deep code reviews.
Other router models	Additional models available via PluggedIn or OpenRouter (e.g., free open‑weights, Gemini).	Use when experimenting or when specific models suit a task.
Vector Memory Choice
This project supports two vector memory backends for semantic recall:
Backend	Description	Pros	Cons
Chroma	An open‑source embedding database that integrates with LangChain and LlamaIndex; scales from notebooks to clusters
datacamp.com
.	Easy to set up locally; good community support; scales horizontally.	Requires local Python environment; not relational.
pgvector	A PostgreSQL extension that adds vector search to a relational database
datacamp.com
.	Leverages existing PostgreSQL infrastructure; allows combining vector and relational queries.	Requires running a PostgreSQL server; scaling vector search may need tuning.
Set the VECTOR_STORE environment variable in setup_mcp_servers.sh to choose either chroma (default) or pgvector. Chroma is recommended for quick setup and hackability
datacamp.com
; pgvector is recommended if your infrastructure already uses PostgreSQL
datacamp.com
.
Context Servers
Server	Purpose	When to Use
Context7	Injects the latest documentation and API references into your prompt
upstash.com
.	Use when coding against external libraries or frameworks; ensures correct API usage.
Sequential Thinking	Helps plan and reason through complex problems by generating and revising a chain of thought
npmjs.com
npmjs.com
.	Use for planning and architecture tasks.
Model Selection Guidelines
Default to local: Start with Gemma for efficiency and privacy. Evaluate the confidence of the response; if low or if the task requires a large context, upgrade to Sonnet.
Use Sonnet sparingly: Sonnet incurs higher costs. Use it only when Gemma cannot handle the scope or when the context window of 64k is required.
Reserve Opus for critical reasoning: When facing architectural choices, complex algorithmic challenges or cross‑module refactoring, use Opus for its deeper reasoning.
Leverage the router: Let PluggedIn or another router decide which model to invoke based on the prompt. This reduces manual switching and ensures cost‑effective decisions.
Monitor token usage: Use context compression and memory servers to keep the context size manageable. If the context grows too large, summarise or store information in Memory Bank instead of leaving it in the conversation.
Safety & Privacy
Local first: Whenever possible, run tasks with the local model to avoid sending sensitive information to cloud services.
Redact before cloud: If you must use a cloud model, ensure that any sensitive data is redacted or pseudonymised. Only the minimum necessary information should be sent.
Adhere to project policies: Comply with non‑functional requirements, security controls and compliance obligations as documented in NON_FUNCTIONAL.md and relevant ADRs.
This file guides the use of language models within the ChatX/ChatRipper project. Update it as new models or context servers become available.