# 🤖 AI Agents: From Zero to Production — Study Plan

> **Language:** Python  
> **Duration:** ~8-10 weeks (adjust to your pace)  
> **Philosophy:** Build → Break → Understand → Deploy  

---

## Phase 1: Foundations (Week 1–2)

### Project 1: Vanilla ReAct Agent (No Framework)
**Goal:** Understand the agent loop from first principles — no LangChain, no LangGraph, just raw Python + LLM API calls.

**Problem Statement:**  
Build a **personal research assistant** that, given a question, can:
1. Decide whether it needs to search the web or can answer directly.
2. If it searches, parse the results and decide if it has enough info or needs another search.
3. Synthesize a final answer with citations.

**What you'll learn:**
- The ReAct (Reason + Act) loop: `Thought → Action → Observation → ... → Final Answer`
- Tool/function calling with raw OpenAI/Anthropic API
- Prompt engineering for agent behavior
- Why frameworks exist (you'll feel the pain of doing it manually)


**Key Concepts to Study:**
- [ReAct Paper](https://arxiv.org/abs/2210.03629)
- [OpenAI Function Calling docs](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic Tool Use docs](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Lilian Weng's "LLM Powered Autonomous Agents" blog post](https://lilianweng.github.io/posts/2023-06-23-agent/)

**Deliverable:** A single Python script (~150-200 lines) that runs in the terminal. Use `httpx` for web search (via Tavily or SerpAPI free tier).

---

### Project 2: Tool-Using Agent with LangGraph
**Goal:** Rebuild Project 1 using LangGraph to understand the graph-based agent paradigm.

**Problem Statement:**  
Build a **code documentation helper** that:
1. Takes a GitHub repo URL as input.
2. Fetches the repo structure (via GitHub API).
3. Reads key files (README, main entry points).
4. Generates a structured summary/documentation of the project.
5. Can answer follow-up questions about the repo.

**What you'll learn:**
- LangGraph's `StateGraph`, nodes, edges, conditional edges
- State management in agent systems
- Tool definition and binding
- Checkpointing basics

**Key Resources:**
- [LangGraph Official Docs](https://langchain-ai.github.io/langgraph/)
- [LangGraph repo examples](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [LangGraph "Quick Start" tutorial](https://langchain-ai.github.io/langgraph/tutorials/introduction/)

**Deliverable:** A LangGraph agent with at least 3 tools (`fetch_repo_structure`, `read_file`, `search_code`). Expose it via a simple CLI.

---

## Phase 2: Memory, State & Persistence (Week 3–4)

### Project 3: Conversational Agent with Memory
**Goal:** Understand short-term (conversation) and long-term (persistent) memory.

**Problem Statement:**  
Build a **personal finance advisor** chatbot that:
1. Remembers your financial goals across sessions (long-term memory).
2. Tracks the current conversation context (short-term memory).
3. Can recall past conversations: "What did I say about my budget last week?"
4. Uses a vector store (ChromaDB or Qdrant) for semantic memory retrieval.
5. Persists state using LangGraph's `SqliteSaver` or `PostgresSaver`.

**What you'll learn:**
- Conversation buffer vs. summary vs. vector-backed memory
- LangGraph checkpointers for persistence
- Embedding models and vector stores
- Memory retrieval strategies (recency, relevance, importance)

**Key Resources:**
- [LangGraph Persistence docs](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [Mem0 — self-improving memory layer](https://github.com/mem0ai/mem0) (study their architecture)
- [Letta (formerly MemGPT)](https://github.com/letta-ai/letta) — memory-focused agent framework
- [ChromaDB docs](https://docs.trychroma.com/)

**Deliverable:** A chatbot that survives restarts. Kill it, restart, and it should remember who you are and your past context.

---

### Project 4: Structured Output & Guardrails
**Goal:** Make agents reliable and predictable.

**Problem Statement:**  
Build an **email triage agent** that:
1. Takes a batch of emails (mock data or Gmail API).
2. Classifies each as: urgent / needs-reply / FYI / spam.
3. Drafts replies for "needs-reply" emails in your tone.
4. Outputs everything as validated Pydantic models.
5. Has guardrails: never leaks PII, stays professional, refuses inappropriate requests.

**What you'll learn:**
- Pydantic + structured output from LLMs
- Input/output validation and guardrails
- Error handling and retry logic in agents
- Content filtering and safety layers

**Key Resources:**
- [Instructor library](https://github.com/instructor-ai/instructor) — structured LLM outputs
- [Guardrails AI](https://github.com/guardrails-ai/guardrails)
- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [NeMo Guardrails by NVIDIA](https://github.com/NVIDIA/NeMo-Guardrails)

**Deliverable:** A pipeline that processes 20+ mock emails and outputs a clean JSON report. Zero crashes, zero malformed outputs.

---

## Phase 3: Multi-Agent Systems (Week 5–6)

### Project 5: Supervisor-Worker Multi-Agent System
**Goal:** Orchestrate multiple specialized agents under a supervisor.

**Problem Statement:**  
Build a **content creation pipeline** with these agents:
1. **Researcher Agent** — searches the web, gathers facts and sources.
2. **Writer Agent** — drafts a blog post from the research.
3. **Editor Agent** — reviews for grammar, tone, factual accuracy.
4. **SEO Agent** — optimizes headings, meta descriptions, keywords.
5. **Supervisor** — orchestrates the workflow, decides when output is good enough.

The supervisor should be able to send work back (e.g., "Editor found issues → Writer revises").

**What you'll learn:**
- Supervisor pattern in multi-agent systems
- Agent-to-agent communication
- LangGraph's `Command` and dynamic routing
- Handling cycles and termination conditions

**Key Resources:**
- [LangGraph Multi-Agent tutorial](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/)
- [LangGraph Supervisor pattern](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/)
- [CrewAI](https://github.com/crewAIInc/crewAI) — study their multi-agent architecture
- [AutoGen by Microsoft](https://github.com/microsoft/autogen) — multi-agent conversations

**Deliverable:** Given a topic, produce a publish-ready blog post. Log every inter-agent message for debugging.

---

### Project 6: Hierarchical Agent Teams
**Goal:** Build nested multi-agent teams where sub-teams handle complex sub-tasks.

**Problem Statement:**  
Build a **startup idea validator** system:
- **Market Research Team:**
  - Competitor Analyst (searches for competitors)
  - Market Size Estimator (finds TAM/SAM/SOM data)
  - Trend Analyzer (identifies market trends)
- **Technical Feasibility Team:**
  - Tech Stack Advisor (suggests architecture)
  - Complexity Estimator (estimates build effort)
- **Financial Team:**
  - Revenue Model Analyst
  - Cost Estimator
- **Top-Level Orchestrator** coordinates all teams and produces a final report.

**What you'll learn:**
- Hierarchical agent orchestration
- Sub-graph composition in LangGraph
- Parallel execution of agent teams
- Aggregating results from multiple agent streams

**Key Resources:**
- [LangGraph Hierarchical Agent Teams](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/hierarchical_agent_teams/)
- [LangGraph Subgraphs](https://langchain-ai.github.io/langgraph/concepts/subgraphs/)
- [OpenAI Swarm](https://github.com/openai/swarm) (lightweight multi-agent, great for studying patterns)

**Deliverable:** Input a startup idea → get a structured feasibility report with sections from each team.

---

## Phase 4: Observability & Evaluation (Week 7)

### Project 7: Add Observability to Project 5 or 6
**Goal:** You can't improve what you can't measure.

**Problem Statement:**  
Instrument your multi-agent system with full observability:
1. **Tracing:** Every LLM call, tool call, and agent step traced end-to-end.
2. **Cost tracking:** Token usage and estimated cost per run.
3. **Latency monitoring:** Time per agent step, identify bottlenecks.
4. **Quality evaluation:** Use LLM-as-judge to score outputs.
5. **Dashboard:** Visualize traces, costs, and quality metrics.

**What you'll learn:**
- Distributed tracing for LLM applications
- LLM evaluation strategies (automated + human-in-the-loop)
- Cost optimization (caching, model routing)
- Setting up observability in practice

**Key Resources & Tools (pick 1-2 to go deep):**
- [LangSmith](https://smith.langchain.com/) — LangChain's observability platform (tight LangGraph integration)
- [Langfuse](https://github.com/langfuse/langfuse) — open-source LLM observability (self-hostable)
- [Arize Phoenix](https://github.com/Arize-AI/phoenix) — open-source LLM traces & evals
- [OpenLLMetry by Traceloop](https://github.com/traceloop/openllmetry) — OpenTelemetry for LLMs
- [Braintrust](https://www.braintrust.dev/) — evals and logging
- [Ragas](https://github.com/explodinggradients/ragas) — RAG evaluation framework (if your agents use RAG)

**Deliverable:** A dashboard (LangSmith or Langfuse) showing traces of your multi-agent runs with cost, latency, and quality scores.

---

## Phase 5: Production Deployment (Week 8–9)

### Project 8: Deploy an Agent as an API
**Goal:** Ship your agent to production behind a REST/streaming API.

**Problem Statement:**  
Take your best agent (Project 5 or 6) and deploy it:
1. Wrap it in a **FastAPI** server with streaming support (SSE).
2. Add **authentication** (API key or JWT).
3. Add **rate limiting** and **request queuing**.
4. Implement **human-in-the-loop**: pause execution, wait for user approval, resume.
5. Deploy to a cloud platform.

**Deployment Targets (pick one):**
- **LangGraph Platform / LangGraph Cloud** — managed deployment for LangGraph agents
- **Modal** — serverless GPU/CPU compute (great for agents)
- **Railway / Render / Fly.io** — simple container deploys
- **AWS Lambda + API Gateway** — serverless (for simpler agents)
- **Docker + any VPS** — full control

**What you'll learn:**
- Streaming agent responses to clients
- Human-in-the-loop patterns
- Agent state management in concurrent environments
- Deployment, scaling, and infrastructure

**Key Resources:**
- [LangGraph Server / Deployment docs](https://langchain-ai.github.io/langgraph/concepts/langgraph_server/)
- [LangGraph Human-in-the-Loop](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
- [FastAPI Streaming Response](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [Modal docs](https://modal.com/docs)
- [LangServe](https://github.com/langchain-ai/langserve) (if using LangChain chains)

**Deliverable:** A publicly accessible API endpoint that runs your agent. Share the URL, call it with `curl`, and see streaming results.

---

### Project 9: Production-Hardened Agent with Full Stack
**Goal:** Build a complete, production-ready agent application.

**Problem Statement:**  
Build a **customer support agent** for a fictional SaaS product:
1. **RAG pipeline** — index product docs, FAQs, past tickets into a vector store.
2. **Multi-turn conversation** — maintains context across messages.
3. **Tool use** — can look up order status (mock API), create tickets, escalate to human.
4. **Fallback strategy** — if the agent is unsure, it escalates gracefully.
5. **Frontend** — simple chat UI (Streamlit, Chainlit, or Next.js).
6. **Observability** — full tracing with Langfuse or LangSmith.
7. **Evaluation suite** — automated test cases that run on every change.
8. **CI/CD** — GitHub Actions pipeline that runs evals before deploying.

**What you'll learn:**
- End-to-end agent application architecture
- RAG + agents combined
- Testing and evaluation in CI/CD
- Production error handling and fallbacks

**Key Resources:**
- [Chainlit](https://github.com/Chainlit/chainlit) — chat UI for LLM apps
- [Streamlit](https://streamlit.io/) — quick UI prototyping
- [LangGraph + RAG tutorial](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_adaptive_rag/)
- [DeepEval](https://github.com/confident-ai/deepeval) — LLM evaluation framework
- [Promptfoo](https://github.com/promptfoo/promptfoo) — prompt/LLM testing

**Deliverable:** A fully deployed chat application with CI/CD, observability, and an eval suite. This is your portfolio piece.

---

## Phase 6: Advanced Topics (Week 10+)

### Project 10: Pick Your Adventure

Choose one (or more) based on your interests:

#### Option A: Code Generation Agent
Build an agent that can write, test, and debug code autonomously.
- Study: [SWE-agent](https://github.com/princeton-nlp/SWE-agent), [OpenHands (formerly OpenDevin)](https://github.com/All-Hands-AI/OpenHands), [Aider](https://github.com/paul-gauthier/aider)

#### Option B: Planning & Execution Agent  
Build an agent that decomposes complex goals into executable plans, adapts when steps fail.
- Study: [Plan-and-Solve paper](https://arxiv.org/abs/2305.04091), [BabyAGI](https://github.com/yoheinakajima/babyagi)

#### Option C: Voice/Multimodal Agent
Build an agent that processes voice input, images, and text.
- Study: [LiveKit Agents](https://github.com/livekit/agents), [Pipecat](https://github.com/pipecat-ai/pipecat)

#### Option D: Agent-to-Agent Communication (A2A Protocol)
Build agents that communicate using Google's Agent2Agent protocol.
- Study: [A2A Protocol](https://github.com/google/A2A)

#### Option E: MCP (Model Context Protocol) Integration
Build agents that connect to external tools/data via MCP servers.
- Study: [MCP Specification](https://modelcontextprotocol.io/), [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

---

## 📚 Overarching Resources

### Must-Read Repositories
| Repo | Why |
|------|-----|
| [LangGraph](https://github.com/langchain-ai/langgraph) | Your primary framework |
| [CrewAI](https://github.com/crewAIInc/crewAI) | Alternative multi-agent patterns |
| [AutoGen](https://github.com/microsoft/autogen) | Microsoft's multi-agent framework |
| [OpenAI Swarm](https://github.com/openai/swarm) | Minimalist multi-agent |
| [Phidata](https://github.com/phidatahq/phidata) | Production-ready agent toolkit |
| [Haystack](https://github.com/deepset-ai/haystack) | Agent pipelines + RAG |
| [Smolagents by HuggingFace](https://github.com/huggingface/smolagents) | Lightweight agents |

### Must-Read Articles & Blogs
- [Anthropic: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) — **Read this first**
- [Lilian Weng: LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/)
- [LangChain: Agent Architectures](https://blog.langchain.dev/what-is-an-agent/)
- [Chip Huyen: Building LLM Applications for Production](https://huyenchip.com/2023/04/11/llm-engineering.html)
- [Jason Wei: Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903)

### YouTube Channels
- **LangChain** — official tutorials
- **AI Jason** — practical agent builds
- **James Briggs** — LangChain/LangGraph deep dives
- **Dave Ebbelaar** — agent engineering

---

## 🗂️ Suggested Project Structure

```
Agents/
├── STUDY_PLAN.md          ← You are here
├── 01_vanilla_react/      ← Project 1
│   ├── agent.py
│   ├── tools.py
│   ├── requirements.txt
│   └── README.md
├── 02_langgraph_basics/   ← Project 2
├── 03_memory_agent/       ← Project 3
├── 04_structured_output/  ← Project 4
├── 05_multi_agent/        ← Project 5
├── 06_hierarchical/       ← Project 6
├── 07_observability/      ← Project 7
├── 08_deployment/         ← Project 8
├── 09_production_app/     ← Project 9
└── 10_advanced/           ← Project 10
```

---

## ✅ How to Use This Plan

1. **Work through projects sequentially** — each builds on the previous.
2. **Don't copy-paste** — type everything yourself, understand every line.
3. **Break things** — intentionally cause failures to understand error handling.
4. **Keep a learning journal** — write down what surprised you in each project.
5. **Read the source code** of frameworks you use (LangGraph internals are enlightening).
6. **Ask for guidance** — when you start each project, I'll give you hints, architecture guidance, and review your approach. I won't hand you the full script.

---

**Ready? Start with Project 1. Set up your Python environment and let me know when you want the detailed kickoff for the vanilla ReAct agent.**
