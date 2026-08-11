
import os 
import json
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from groq import Groq

from retriever import IncidentRetriever
from tools import TOOLS_SCHEMA, execute_tool_call

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from envoirmnet variables!")

# ---- Pydancic Schema Definition ----------
class MatchingPostMortem(BaseModel):
    title:str = Field(description="Title of the matching historical post-mortem")
    similarity_score: float = Field(description="Cosine Similarity of the match (0.0 to 1.0)")
    link_or_ref: str = Field(description="Source filename or reference link")

class IncidentTriageReport(BaseModel):
    incident_title: str = Field(description="Short description title of the incident")
    severity: str = Field(description="Severity classification: P1_CRITICAL, P2_HIGH, P3_MEDIUM, or P4_LOW")
    root_cause_analysis: str = Field(description="Detailed technical root cause analysis combining error logs, RAG matches, and telemetry metrics")
    matching_historical_postmortem: Optional[MatchingPostMortem] = Field(description="Best matching historical incident from RAG search, if relevant")
    infra_tool_check_results: str = Field(description="Summary of telemetry/metrics retrieved via tool calls (or 'No Tool check requires')")
    recommended_mitigation_steps: List[str] = Field(description="List of actionaable step-by-step remediation instructions")

# ---- Main Triage Engine Orchestration ----------
class IncidentTriageEngine:
    """Orchestrates RAG retrievel, Tool Calling, and structured JSON synthesis via Groq Llama 3.3."""

    def __init__(self, model_name: str ="llama-3.3-70b-versatile"):
        self.model_name = model_name
        print("Initializing Groq API Clients...")
        self.client = Groq(api_key=GROQ_API_KEY)

        print("Initializing RAG Retriever...")
        self.retriever = IncidentRetriever(top_k=2)

    def analyze_incident(self, raw_log: str) -> IncidentTriageReport:
        """Runs end-to-end triage pipeline for an incoming log string."""
        print("Step 1: Performing RAG search against Pinecone...")
        rag_matches = self.retriever.search_similar_incidents(raw_log)

        # Format retrieved RAG context for prompt injection
        rag_context_str = ""
        top_match = None
        if rag_matches: 
            top_match = rag_matches[0]
            rag_context_str = "\n".join([
                f"- [Score: {m['score']}] {m['title']} ({m['company']}): {m['text'][:300]}"
                for m in rag_matches
            ])
        else:
            rag_context_str = "No historical post-mortems matched."

        system_prompt = f"""You are an expert Site Reliability Engineer (SRE) and Incident Response Agent.
Your job is to analyze raw crash logs, inspect live infrastructure telemetry, and generate a structured incident report.

Target Response Schema (JSON):
{json.dumps(IncidentTriageReport.model_json_schema(), indent=2)}

Guidelines:
1. Severity Scale: P1_CRITICAL (Outage/Data Loss), P2_HIGH (Degraded Service/high error rate), P3_MEDIUM (Non-critical failures), P4_LOW (Warnings/minor bugs).
2. If the log contains server IPs (e.g., '10.0.0.4') or service names (e.g., 'auth-service'), use the provided tools to inspect telemetry and deployments before finalizing your report.
3. Your output MUST be a single, valid JSON object strictly matching the schema above.
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Incoming Crash Log:\n```\n{raw_log}\n```\n\nMatching Historical Post-Mortems (RAG):\n{rag_context_str}"}
        ]

        # SFirst LLM Call (Evaluates log and decides if the Tool Calls are needed)
        print("Step 2: Querying Groq LLM (evaluating tool calls)...")
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
            temperature=0.1
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        tool_results_summary = "No infrastructure tool checks executed."

        if tool_calls:
            print(f"Step 3: Executing {len(tool_calls)} Tool Call(s) requested by Groq...")
            messages.append(response_message)

            executed_tool_outputs = []
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                print(f" Tool Executed: {function_name}{function_args}")
                tool_output = execute_tool_call(function_name, function_args)
                executed_tool_outputs.append(f"{function_name}: {tool_output}")

                # append tool response back to LLM conversation
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": tool_output
                })

            tool_results_summary = " | ".join(executed_tool_outputs)

            print("Step 4: Synthesizing final report with tool output...")
            final_response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1
            )
            raw_json_output = final_response.choices[0].message.content
        else:
            print("Step 3: No tool calls required. Forcing JSON synthesis...")
            # If no tool calls, re-prompt for structured JSON output
            messages.append({"role": "user", "content": "Now generate the final incident report adhering strictly to the JSON schema."})
            final_response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1
            )
            raw_json_output = final_response.choices[0].message.content

        print("Step 5: Validating Response against Pydantic Schema...")
        parsed_json = json.loads(raw_json_output)

        # ensure matching_historical_postmortem field is populated correctly from RAG
        if top_match and "matching_historical_postmortem" in parsed_json:
            parsed_json["matching_historical_postmortem"] = {
                "title": top_match["title"],
                "similarity_score": top_match["score"],
                "link_or_ref": top_match["source"]
            }

        report = IncidentTriageReport(**parsed_json)
        return report

if __name__ == "__main__":
    engine = IncidentTriageEngine()
    sample_crash_log = """
2026-08-08 14:02:11.108 UTC [9921] ERROR: sqlalchemy.exc.OperationalError: 
(psycopg2.OperationalError) FATAL: max_connections reached on host 10.0.0.4:5432
Application auth-service failed to obtain active connection handle. Worker thread crashed.
"""

    print(f"\n --- Testing Incident Triage Engine ----")
    print(f"Input Log Snippet:\n{sample_crash_log.strip()}\n")

    report = engine.analyze_incident(sample_crash_log)

    print("\n" + "="*50)
    print("GENERATED STRUCTURED INCIDENT REPORT")
    print("="*50)
    print(json.dumps(report.model_dump(), indent=2))




