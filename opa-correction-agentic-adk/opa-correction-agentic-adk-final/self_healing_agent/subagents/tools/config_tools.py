"""
Configuration tools for accessing environment configuration within agents.
"""

from typing import Dict, Any
from google.adk.tools import FunctionTool, ToolContext
from self_healing_agent.config import get_github_token, get_github_repo_url, get_max_iterations


def get_github_config(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Get GitHub configuration from environment or state.
    
    This tool checks for github_token and github_repo_url in:
    1. Tool context state (runtime override)
    2. Environment variables from .env file (default)
    
    Args:
        tool_context: ADK tool context
        
    Returns:
        dict with github_token, github_repo_url, and availability status
    """
    try:
        # Check state first (runtime override)
        state_token = tool_context.state.get("github_token")
        state_repo_url = tool_context.state.get("github_repo_url")
        
        # Use state values or fall back to config
        github_token = state_token or get_github_token()
        github_repo_url = state_repo_url or get_github_repo_url()
        
        # Update state with the values being used
        if github_token:
            tool_context.state["github_token"] = github_token
        if github_repo_url:
            tool_context.state["github_repo_url"] = github_repo_url
        
        # Also set max_iterations from config if not in state
        if "max_iterations" not in tool_context.state:
            tool_context.state["max_iterations"] = get_max_iterations()

        # Set policy_path from config if not in state
        if "policy_path" not in tool_context.state:
            from self_healing_agent.config import get_policy_path
            tool_context.state["policy_path"] = get_policy_path()
        
        # IMPORTANT: Return the actual token value so the agent can use it!
        return {
            "status": "success",
            "github_token": github_token or "NOT_CONFIGURED",  # Return actual token value
            "github_token_available": bool(github_token),
            "github_repo_url": github_repo_url or "Not configured",
            "max_iterations": tool_context.state.get("max_iterations", 5),
            "policy_path": tool_context.state.get("policy_path"),
            "source": {
                "token": "state" if state_token else "env",
                "repo_url": "state" if state_repo_url else "env"
            },
            "message": f"Configuration loaded successfully. Token length: {len(github_token) if github_token else 0}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to load configuration: {str(e)}",
            "error_type": type(e).__name__
        }


# Create tool instance
get_github_config_tool = FunctionTool(func=get_github_config)

