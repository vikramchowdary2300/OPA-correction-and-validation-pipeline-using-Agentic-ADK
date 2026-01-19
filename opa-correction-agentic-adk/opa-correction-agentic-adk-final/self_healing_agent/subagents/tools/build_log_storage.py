"""
ADK Tool for storing build logs from log text to ADK state.
"""

from google.adk.tools import FunctionTool, ToolContext


def store_build_logs(tool_context: ToolContext, log_text: str) -> dict:
    """
    Process log text and store only build logs to the ADK state.
    
    This tool analyzes the provided log text, identifies build-related logs,
    and stores them in the ADK state for future reference.
    
    Args:
        tool_context: The ADK tool context that provides access to state
        log_text: The complete log text to be analyzed
        
    Returns:
        A dictionary containing the status and number of build logs stored
    """
    if not log_text or not log_text.strip():
        return {
            "status": "error",
            "message": "No log text provided",
            "build_logs_count": 0
        }
    
    # Split the log text into individual lines
    log_lines = log_text.splitlines()
    
    # Filter lines that are related to build logs
    # Common build-related keywords: build, compile, make, cmake, gradle, maven, npm, etc.
    build_keywords = [
        "build", "compile", "compiling", "compilation",
        "make", "cmake", "gradle", "maven", "npm",
        "yarn", "webpack", "bundling", "linking",
        "assembling", "building", "built"
    ]
    
    build_logs = []
    for line in log_lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in build_keywords):
            build_logs.append(line.strip())
    
    if not build_logs:
        return {
            "status": "success",
            "message": "No build logs found in the provided text",
            "build_logs_count": 0
        }
    
    # Store the filtered build logs in the ADK state
    # If there are existing build logs, we append to them
    existing_logs = tool_context.state.get("build_logs", [])
    
    # Ensure existing_logs is a list
    if not isinstance(existing_logs, list):
        existing_logs = []
    
    # Append new build logs
    existing_logs.extend(build_logs)
    
    # Store back to state
    tool_context.state["build_logs"] = existing_logs
    
    return {
        "status": "success",
        "message": "Build logs processed and stored successfully",
        "build_logs_count": len(build_logs),
        "total_logs_in_state": len(existing_logs)
    }


# Create the ADK Tool instance
# The description is taken from the function's docstring automatically
build_log_storage_tool = FunctionTool(func=store_build_logs)

