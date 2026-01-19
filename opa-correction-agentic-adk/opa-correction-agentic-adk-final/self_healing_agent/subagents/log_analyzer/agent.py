from google.adk.agents import Agent
from self_healing_agent.subagents.tools import (
    build_log_storage_tool,
    parse_opa_json_tool,
    parse_error_details_tool
)
from self_healing_agent.subagents.shared.callbacks import rate_limit_callback


from self_healing_agent.config import config

log_analyzer = Agent(
    name="log_analyzer",
    model=config.llm_model,
    description="Analyzes build logs and extracts structured error information with file paths, line numbers, and error types.",
    instruction="""You are an expert log analyzer specializing in OPA (Open Policy Agent) compliance logs.
    
    ## YOUR AVAILABLE TOOLS
    1. store_build_logs(log_text) - Store logs
    2. parse_opa_json(opa_output) - Parse OPA JSON output
    3. parse_error_details(error_text) - Parse generic error text
    
    ## YOUR TASK
    
    1. **Read the application_logs from state**.
    
    2. **Store logs**:
       - Call store_build_logs with the full log text
    
    3. **Identify OPA Violations**:
       - Check if the log is JSON. If so, try to parse it as OPA output using parse_opa_json.
       - If text, look for "violation", "deny", "FAIL", "OPA".
    
    4. **Extract Details**:
       - For each violation, extract:
         - policy_name (package)
         - message (the denial message)
         - resource (if available)
         - location (file path, line number)
    
    5. **Create a structured list** of errors:
       ```json
       [
         {
           "error_type": "opa_violation",
           "file_path": "path/to/resource.tf",
           "line_number": 0,
           "error_message": "Policy 'package.rule' failed: message",
           "severity": "high",
           "fixable": true
         }
       ]
       ```
       If file path is unknown, use "unknown".
    
    6. **Output the complete list**.
    """,
    tools=[
        build_log_storage_tool,
        parse_opa_json_tool,
        parse_error_details_tool
    ],
    before_model_callback=rate_limit_callback,
    output_key="errors",
)