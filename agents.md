agents.md — AI Agent Guidelines for ChatX/ChatRipper
Status: Draft | Owner: <TBD> | Last Updated: 2025‑09‑02
Purpose
This document defines the roles and responsibilities of various AI agents used in the ChatX/ChatRipper project. Each agent utilises specific MCP tools to accomplish its tasks. Adhering to these definitions helps maintain clarity and reproducibility in AI‑assisted development.
Agent Roles
Agent	Responsibilities	MCP Tools
Planner	Analyse requirements, create user stories, define acceptance criteria, and break tasks into manageable slices.	Sequential Thinking
npmjs.com
npmjs.com
, Context7
upstash.com
, Notion
apidog.com
Coder	Implement features and fixes according to the plan, write tests, and refactor for readability.	Filesystem
mcpservers.org
, GitHub
apidog.com
, Pandoc, Vector Memory (LanceDB/Chroma/pgvector)
Tester	Execute test suites, evaluate coverage and performance, and report failures.	Filesystem, GitHub
Researcher	Perform external research for libraries, examples and best practices; gather information for design decisions.	Exa
apidog.com
, DuckDuckGo, MCP Compass
Memory Manager	Store, organise and retrieve knowledge about the project; update Memory Bank and Knowledge Graph Memory.	Memory Bank, Knowledge Graph Memory, Memory MCP
mcpmarket.com
Router	Decide which model to use for a given task (Gemma, Sonnet, Opus) and compress context when necessary.	PluggedIn Proxy
Agent Usage
Planner
Consult sequential thinking and context servers to gather requirements and create an actionable plan.
Record acceptance criteria and open questions in Memory Bank.
Coder
Read the relevant files via Filesystem or GitHub.
Write tests first; then implement minimal diffs; commit using GitHub MCP.
Use vector memory to recall past patterns and align with code standards.
Tester
Run test commands (e.g., npm test, pytest) and collect results.
Create detailed bug reports in Memory Bank or Notion.
Researcher
Use Exa or DuckDuckGo servers to obtain external information and examples.
Summarise findings and store them in Memory Bank for future retrieval.
Memory Manager
Organise project notes into Memory Bank and Knowledge Graph Memory.
Update the knowledge graph when new relationships or concepts are identified.
Router
Monitor model usage and context length. When the conversation becomes long, trigger the PluggedIn proxy to compress context and choose the appropriate model.
Guidelines
Agents MUST always read CLAUDE.md and repo_prompt.md at the start of a session to understand the project context.
Agents MUST avoid executing commands or making changes outside their scope. For example, the Researcher should not modify files.
Agents MUST request human confirmation before performing destructive operations (e.g., deleting branches or dropping tables).
Agents SHOULD persist all non‑trivial findings or decisions in Memory Bank or Knowledge Graph Memory for future sessions.
Agents MAY collaborate by passing context through Memory Bank rather than through long prompt chains.
This document will evolve as new agents or tools are introduced. Keep it up to date to maintain clarity in multi‑agent workflows.
