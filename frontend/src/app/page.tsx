"use client";

import { useState } from "react";
import { 
  AlertTriangle, 
  CheckCircle2, 
  Terminal, 
  Cpu, 
  Database, 
  ArrowRight, 
  Loader2, 
  Sparkles,
  ShieldAlert
} from "lucide-react";
import { analyzeLog, IncidentTriageReport } from "@/lib/api";

const SAMPLE_LOG = `2026-08-08 14:02:11.108 UTC [9921] ERROR: sqlalchemy.exc.OperationalError: 
(psycopg2.OperationalError) FATAL: max_connections reached on host 10.0.0.4:5432
Application auth-service failed to obtain active connection handle. Worker thread crashed.`;

export default function IncidentDashboard() {
  const [logInput, setLogInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<IncidentTriageReport | null>(null);

  const handleTriage = async () => {
    if (!logInput.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const data = await analyzeLog(logInput);
      setReport(data);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred during triage.");
    } finally {
      setLoading(false);
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "P1_CRITICAL":
        return "bg-red-500/10 text-red-400 border-red-500/30";
      case "P2_HIGH":
        return "bg-orange-500/10 text-orange-400 border-orange-500/30";
      case "P3_MEDIUM":
        return "bg-yellow-500/10 text-yellow-400 border-yellow-500/30";
      default:
        return "bg-blue-500/10 text-blue-400 border-blue-500/30";
    }
  };

  return (
    <main className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Top Header */}
      <header className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-600/20 rounded-xl border border-indigo-500/30 text-indigo-400">
            <ShieldAlert className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">Automated Incident Triage Engine</h1>
            <p className="text-xs text-slate-400">AI-Powered Log Analysis • Pinecone RAG • Groq Agentic Telemetry</p>
          </div>
        </div>
        <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-full">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-medium text-emerald-400">Engine Online</span>
        </div>
      </header>

      {/* Main Grid: Input Console (Left) vs Report Panel (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Log Input & Controls */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
                <Terminal className="w-4 h-4 text-indigo-400" />
                Raw Log / Stack Trace
              </div>
              <button
                onClick={() => setLogInput(SAMPLE_LOG)}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
              >
                Load Sample Log
              </button>
            </div>

            <textarea
              value={logInput}
              onChange={(e) => setLogInput(e.target.value)}
              placeholder="Paste error logs, stack traces, or panic outputs here..."
              rows={12}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs font-mono text-slate-300 focus:outline-none focus:border-indigo-500 resize-none"
            />

            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-xs text-red-400 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                {error}
              </div>
            )}

            <button
              onClick={handleTriage}
              disabled={loading || !logInput.trim()}
              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-500 text-white font-medium py-2.5 px-4 rounded-lg text-sm transition-all flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Running Triage Engine...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Run Incident Analysis
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Triage Report Results */}
        <div className="lg:col-span-7">
          {report ? (
            <div className="space-y-6">
              {/* Incident Title & Severity Card */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Incident Title</span>
                    <h2 className="text-xl font-bold text-white mt-1">{report.incident_title}</h2>
                  </div>
                  <span className={`px-3 py-1 rounded-md text-xs font-semibold border ${getSeverityBadge(report.severity)}`}>
                    {report.severity}
                  </span>
                </div>

                <hr className="border-slate-800" />

                {/* Root Cause Analysis */}
                <div>
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Root Cause Analysis</h3>
                  <p className="text-sm text-slate-300 leading-relaxed bg-slate-950 p-4 rounded-lg border border-slate-800/60 font-mono">
                    {report.root_cause_analysis}
                  </p>
                </div>
              </div>

              {/* RAG Match & Telemetry Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Historical RAG Match */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                  <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    <Database className="w-4 h-4 text-emerald-400" />
                    Historical Post-Mortem Match
                  </div>
                  {report.matching_historical_postmortem ? (
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-white">{report.matching_historical_postmortem.title}</p>
                      <div className="flex items-center justify-between text-xs text-slate-400">
                        <span>Similarity Score</span>
                        <span className="font-mono text-emerald-400 font-bold">
                          {(report.matching_historical_postmortem.similarity_score * 100).toFixed(1)}%
                        </span>
                      </div>
                      <p className="text-xs font-mono text-slate-500 truncate">
                        Ref: {report.matching_historical_postmortem.link_or_ref}
                      </p>
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500">No matching historical incident found above similarity threshold.</p>
                  )}
                </div>

                {/* Infrastructure Tool Check Results */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                  <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    <Cpu className="w-4 h-4 text-sky-400" />
                    Live Telemetry Check
                  </div>
                  <p className="text-xs font-mono text-slate-300 leading-relaxed bg-slate-950 p-3 rounded-lg border border-slate-800">
                    {report.infra_tool_check_results}
                  </p>
                </div>
              </div>

              {/* Recommended Mitigation Steps */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Recommended Action Steps</h3>
                <ul className="space-y-2.5">
                  {report.recommended_mitigation_steps.map((step, idx) => (
                    <li key={idx} className="flex items-start gap-3 bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                      <CheckCircle2 className="w-4 h-4 text-indigo-400 mt-0.5 shrink-0" />
                      <span className="text-xs text-slate-200">{step}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            /* Empty State Placeholder */
            <div className="bg-slate-900/50 border border-dashed border-slate-800 rounded-xl p-12 text-center flex flex-col items-center justify-center min-h-[420px]">
              <div className="p-3 bg-slate-800/50 rounded-full text-slate-500 mb-4">
                <Terminal className="w-8 h-8" />
              </div>
              <h3 className="text-sm font-semibold text-slate-300">Awaiting Log Submission</h3>
              <p className="text-xs text-slate-500 max-w-sm mt-1">
                Paste an operational crash log or click "Load Sample Log" on the left console to generate a triage report.
              </p>
            </div>
          )}
        </div>

      </div>
    </main>
  );
}