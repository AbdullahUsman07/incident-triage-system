
import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from dotenv import load_dotenv

from src.triage_engine import IncidentTriageEngine, IncidentTriageReport

env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

app = FastAPI(
    title="Automated Incident Triage API",
    description="Backend microservice for log analysis using Pinecone RAG, Groq Tool Calling, and Pydantic Schemas",
    version="1.0.0",
)

# Enable CORS for Next.js frontend (vercel and local host)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engine instance
triage_engine: Optional[IncidentTriageEngine] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global triage_engine

    print("Booting up FastAPI service & Initializing Triage Engine...")
    triage_engine = IncidentTriageEngine()

    yield 

app = FastAPI(lifespan=lifespan)

class LogPayload(BaseModel):
    log_text: str

@app.get("/api/health", tags=["Health"])
def health_check():
    """Endpoint for monitoring service health."""
    return {
        "status":"online",
        "service":"Automated Incident Triage Microservice",
        "engine_ready":triage_engine is not None 
    }

@app.post("/api/triage", response_model=IncidentTriageReport, tags=["Triage"])
def triage_log_text(payload: LogPayload):
    """Processes raw log text submitted via JSON payload."""
    if not payload.log_text or not payload.log_text.strip():
        raise HTTPException(status_code=400, detail="the log_text parameter cannot be empty.")

    if not triage_engine:
        raise HTTPException(status_code=503, detail="Triage Engine is not Initialized yet.")

    try: 
        report = triage_engine.analyze_incident(payload.log_text)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage Execution Failed: {str(e)}")

@app.post("/api/triage/upload", response_model=IncidentTriageReport, tags=["Triage"])
async def triage_log_file(file: UploadFile = File(...)):
    """Processes an uploaded log or stack trace file (.log or .txt)"""
    if not file.filename.endswith(('.log','.txt','.out','.json')):
        raise HTTPException(status_code=400,detail="Invalid file type. Please upload a .log or .txt file.")

    if not triage_engine: 
        raise HTTPException(status_code=503, detail="Triage engine is not initialized yet.")

    try: 
        content = await file.read()
        log_text = content.decode("utf-8", errors="ignore")

        if not log_text.strip():
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        report = triage_engine.analyze_incident(log_text)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")