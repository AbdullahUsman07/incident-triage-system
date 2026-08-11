
export interface MatchingPostMortem {
    title: string;
    similarity_score: number;
    link_or_ref: string;
}

export interface IncidentTriageReport {
    incident_title: string;
    severity: "P1_CRITICAL" | "P2_HIGH" | "P3_MEDIUM" | "P4_LOW" | string;
    root_cause_analysis: string;
    matching_historical_postmortem?: MatchingPostMortem;
    infra_tool_check_results: string;
    recommended_mitigation_steps: string[];
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function analyzeLog(logText: string): Promise<IncidentTriageReport> {
    const response = await fetch(`${API_BASE_URL}/api/triage`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ log_text: logText }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Network request failed" }));
        throw new Error(errorData.detail || "Failed to analyze incident log.");
    }

    return response.json();
}