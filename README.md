# 🚨 Automated Crash Log & Incident Triage System

An AI-powered DevOps and SRE triage engine that analyzes raw production stack traces, cross-references historical post-mortems via **RAG (Retrieval-Augmented Generation)**, executes **Autonomous Tool Calls** to inspect live infrastructure telemetry, and generates structured incident reports.

---

## 📌 Key Features & Architecture

- **Unified Frontmatter & Stacktrace Chunker:** Custom parser (`LogAwareChunker`) that strips YAML frontmatter metadata, preserves multi-line error stack traces, and adaptively splits Markdown post-mortems into context-dense chunks.
- **Dense Vector Search (RAG):** Embeds historical Root Cause Analyses (RCAs) using Hugging Face's `all-MiniLM-L6-v2` (384-dim) and indexes them into **Pinecone Serverless Vector DB**.
- **Agentic LLM Tool Calling:** Uses Groq (`Llama-3.3-70b-versatile`) to dynamically call infrastructure telemetry tools (`check_server_health` and `get_recent_deploys`) based on IPs and microservices detected in the crash log.
- **Strict Pydantic JSON Enforcement:** Enforces validated structured output including severity levels (`P1_CRITICAL` to `P4_LOW`), technical root cause analysis, matching historical RAG score, live telemetry summary, and step-by-step remediation steps.
- **FastAPI Backend Microservice:** REST API handling JSON payloads and file uploads (`.log`, `.txt`) with built-in CORS middleware.
- **Next.js SRE Dashboard:** Interactive UI built with Next.js (App Router), TypeScript, Tailwind CSS, and Lucide React icons.

---

## 🛠 Tech Stack

- **LLM Engine:** Groq API (`llama-3.3-70b-versatile`)
- **Embeddings:** Hugging Face `SentenceTransformers` (`all-MiniLM-L6-v2`)
- **Vector Database:** Pinecone Cloud (Serverless, Cosine Metric)
- **Backend Framework:** Python 3.10+, FastAPI, Uvicorn, Pydantic v2
- **Frontend Framework:** Next.js 16 (App Router), TypeScript, Tailwind CSS, Lucide React

---

## 📂 Repository Structure

```text
incident-triage-system/
├── backend/
│   ├── data/
│   │   ├── post_mortems/       # Historical incident reports (.md)
│   │   └── raw_logs/           # System logs from Loghub (.log)
│   ├── src/
│   │   ├── __init__.py
│   │   ├── chunker.py          # Unified Frontmatter & Log-Aware chunker
│   │   ├── ingest.py           # Embeds and indexes post-mortems into Pinecone
│   │   ├── retriever.py        # Pinecone similarity search module
│   │   ├── tools.py            # Infrastructure mock tools & function schemas
│   │   └── triage_engine.py    # Core Agentic loop (RAG + Tools + Pydantic JSON)
│   ├── main.py                 # FastAPI microservice REST endpoints
│   ├── .env                    # API Keys (GROQ_API_KEY, PINECONE_API_KEY)
│   └── requirements.txt        # Backend dependencies
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── globals.css     # Global styles & Tailwind CSS
│   │   │   ├── layout.tsx      # Root layout
│   │   │   └── page.tsx        # Interactive SRE Incident Dashboard
│   │   └── lib/
│   │       └── api.ts          # API fetch client for FastAPI backend
│   ├── .env.local              # Frontend environment variables
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── .gitignore
└── README.md