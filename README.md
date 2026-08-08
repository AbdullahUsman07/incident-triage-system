# 🚨 Automated Crash Log & Incident Triage System

An AI-powered DevOps triage system that analyzes raw production stack traces, cross-references historical post-mortems via **RAG (Retrieval-Augmented Generation)**, queries infrastructure health APIs via **LLM Function Calling**, and generates structured incident response reports.

---

## 📌 Features & System Architecture

- **Log-Aware Chunking:** Custom parser that preserves multi-line stack traces and error blocks without splitting frames across chunk boundaries.
- **RAG via Vector Search:** Embeds historical Root Cause Analyses (RCAs) and post-mortems using `all-MiniLM-L6-v2` and stores them in **Pinecone Cloud**.
- **LLM Function Calling:** Simulates live infrastructure status inspection (e.g., checking database pools, memory spikes, or DNS records).
- **Structured JSON Schema:** Enforces strict Pydantic JSON outputs detailing incident title, P1-P4 severity level, root cause analysis, matching historical incidents, and remediation steps.

---

## 🛠 Tech Stack

- **LLM Engine:** Groq API (`Llama-3.3-70b-versatile`)
- **Embeddings:** Hugging Face `SentenceTransformers` (`all-MiniLM-L6-v2` - 384 dimensions)
- **Vector Database:** Pinecone Serverless
- **Backend Services:** Python 3.10+, FastAPI (Phase 3)
- **Frontend UI:** Next.js, Tailwind CSS, Shadcn UI (Phase 4)

---

## 📂 Repository Structure

```text
incident-triage-system/
├── backend/
│   ├── data/
│   │   ├── post_mortems/       # Downloaded full-text incident reports (.md)
│   │   └── raw_logs/           # Real system logs from Loghub (.log)
│   ├── src/
│   │   ├── __init__.py
│   │   ├── chunker.py          # Custom stacktrace-aware chunking engine
│   │   ├── retriever.py        # Pinecone similarity search
│   │   └── ingest.py           # Vector embedding and indexing script
│   ├── download_data.py        # Automated dataset downloader
│   ├── .env                    # API keys (Groq & Pinecone)
│   └── requirements.txt        # Backend Python dependencies
├── .gitignore
└── README.md