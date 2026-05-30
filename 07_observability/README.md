# Project 7: Observability & Evaluation

Full tracing, cost tracking, and quality evaluation for agent systems using LangSmith.

## Setup

Add to your `.env` file:
```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=startup-validator
```

## Files

| File | Purpose |
|------|---------|
| `main.py` | Runs Project 6 with LangSmith tracing + per-node latency tracking |
| `evaluate.py` | LLM-as-judge evaluation — scores report quality on 5 dimensions |
| `dashboard.py` | Fetches and displays trace data (tokens, cost, latency) from LangSmith |

## Usage

```bash
# 1. Run the pipeline with observability
python main.py

# 2. View trace data and costs
python dashboard.py

# 3. Evaluate report quality (paste the final report when prompted)
python evaluate.py
```

## What's Instrumented

- **Auto-tracing** — Every LLM call, tool call, and graph step traced via LangSmith env vars
- **Custom metadata** — Startup idea and project tags attached to each trace
- **Per-node latency** — CLI shows duration for each team + total pipeline time
- **Cost tracking** — LangSmith auto-captures token usage and cost per LLM call
- **LLM-as-judge** — Structured evaluation scoring completeness, accuracy, actionability, clarity, critical thinking
- **Dashboard** — CLI tool to query LangSmith API for recent runs, tokens, and costs
