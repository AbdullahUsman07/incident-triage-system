import json
from typing import Any, Dict

# Mock Insfrastructure Functions

MOCK_SERVERS = {
    "10.0.0.4": {
        "hostname": "db-primary-01",
        "service": "PostgreSQL-Primary",
        "status": "CRITICAL",
        "cpu_usage_pct": 98.4,
        "memory_usage_pct": 87.1,
        "active_connections": 100,
        "max_connections": 100,
        "disk_usage_pct": 62.0
    },
    "10.0.0.5": {
        "hostname": "redis-cache-01",
        "service": "Redis-Cluster",
        "status": "HEALTHY",
        "cpu_usage_pct": 14.2,
        "memory_usage_pct": 42.0,
        "active_connections": 120,
        "max_connections": 10000,
        "disk_usage_pct": 18.5
    },
    "10.0.0.12": {
        "hostname": "k8s-worker-node-03",
        "service": "Worker-Pod-Cluster",
        "status": "DEGRADED",
        "cpu_usage_pct": 76.0,
        "memory_usage_pct": 99.2,
        "active_connections": 45,
        "max_connections": 500,
        "disk_usage_pct": 94.8
    }
}

MOCK_DEPLOYS = {
    "auth-service": {
        "latest_version": "v2.4.1",
        "deployed_at": "10 minutes ago",
        "author": "devops-bot",
        "git_commit": "a7f3b1c",
        "commit_message": "Update DB connection pool timeout settings"
    },
    "image-processor": {
        "latest_version": "v1.8.0",
        "deployed_at": "2 hours ago",
        "author": "alex@company.com",
        "git_commit": "f9e2d4a",
        "commit_message": "Add batch processing for high-res PNGs"
    },
    "api-gateway": {
        "latest_version": "v3.1.0",
        "deployed_at": "1 day ago",
        "author": "sarah@company.com",
        "git_commit": "c3b8e1f",
        "commit_message": "Rotate SSL certificates and update ingress rules"
    }
}

def check_server_health(ip_address: str) -> str:  
    """Queries live metrics (CPU, Memory, Connections) for a server IP address"""
    server = MOCK_SERVERS.get(ip_address)
    if server: 
        return json.dumps(server)
    return json.dumps({
        "ip_address": ip_address,
        "status": "UNKNOWN_HOST",
        "message": "Host not found in active telemetry registry. Assuming default metrics."
    })

def get_recent_deploys(service_name: str) -> str:
    """Retrives the most recent software deployment metadata for a microservice."""
    deploy = MOCK_DEPLOYS.get(service_name.lower())
    if deploy:
        return json.dumps({"service": service_name, **deploy})
    return json.dumps({
        "service": service_name,
        "status": "NO_RECENT_DEPLOYS",
        "message": f"No recent deployment records found for service '{service_name}' in the last 48 hours."
    })

# Tool Execution Router
AVAILABLE_TOOLS = {
    "check_server_health": check_server_health,
    "get_recent_deploys": get_recent_deploys
}

def execute_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Executes the tool executed by LLM and returns the String response."""
    func = AVAILABLE_TOOLS.get(tool_name)
    if func: 
        try:
            return func(**arguments)
        except Exception as e:
            return json.dumps({"error": f"Failed to execute {tool_name}: {str(e)}"})
    return json.dumps({"error": f"Tool '{tool_name}' is not registered."})

# Groq function tool Schemas 
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "check_server_health",
            "description": "Retrieves real-time telemetry metrics (CPU, Memory, DB Connection usage, Disk) for a specific server IP address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ip_address": {
                        "type": "string",
                        "description": "The IPv4 address extracted from the crash log (e.g., '10.0.0.4')."
                    }
                },
                "required": ["ip_address"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_deploys",
            "description": "Retrieves the latest deployment history, commit hash, author, and timestamp for a microservice.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "The name of the service or component (e.g., 'auth-service', 'image-processor', 'api-gateway')."
                    }
                },
                "required": ["service_name"]
            }
        }
    }
]

if __name__ == "__main__":
    print('Testing Tool Calling Execution:\n')

    res1 = execute_tool_call("check_server_health", {"ip_address": "10.0.0.4"})
    print(f"1. check_server_health('10.0.0.4') ->\n   {res1}\n")

    res2 = execute_tool_call("get_recent_deploys", {"service_name": "auth-service"})
    print(f"2. get_recent_deploys('auth-service') ->\n   {res2}\n")