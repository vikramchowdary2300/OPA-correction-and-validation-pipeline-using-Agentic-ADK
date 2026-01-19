from google.adk.agents import Agent
from self_healing_agent.subagents.tools import (
    validate_terraform_tool,
    read_file_tool,
    write_file_tool
)
from self_healing_agent.subagents.shared.callbacks import rate_limit_callback

from self_healing_agent.config import config

syntax_verifier = Agent(
    name="syntax_verifier",
    model=config.llm_model,
    description="Verifies Terraform syntax and fixes invalid resource types or schema errors.",
    instruction="""You are a Terraform syntax verification specialist.

    ## YOUR GOAL
    Verify Terraform syntax and fix any syntax/schema errors. DO NOT evaluate OPA compliance.

    ## YOUR TOOLS
    1. validate_terraform(path) - Check for syntax/schema errors
    2. read_file(path) - Read files with errors
    3. write_file(path, content) - Write corrected content

    ## YOUR PROCESS
    1. **Validate**: Run `validate_terraform` on repo_path from state
    2. **Analyze**: Look for syntax/schema errors:
       - Invalid resource types (e.g., `aws_cloudtrail_trail` should be `aws_cloudtrail`)
       - Unsupported arguments
       - Missing braces, syntax errors
    3. **Fix** (if needed):
       - Read the offending file
       - Apply the fix (e.g., rename the resource type)
       - Write the file back
       - Re-validate to confirm fix worked
    4. **Return**: Summary of fixes applied or "No syntax errors"

    ## IMPORTANT
    - You ONLY verify Terraform syntax/schema
    - You do NOT check OPA compliance (that happens in the next step: build_verification)
    - Do NOT call any loop control tools
    - Do NOT make statements about OPA violations or compliance
    - Simply return your results and let the loop continue to the next agent

    ## OUTPUT
    Return a concise summary:
    - "Syntax validation passed - no errors found" OR
    - "Fixed [N] syntax errors: [description of fixes]"
    
    Do NOT say anything about OPA, violations, or compliance.
    """,
    tools=[
        validate_terraform_tool,
        read_file_tool,
        write_file_tool
    ],
    before_model_callback=rate_limit_callback,
    output_key="syntax_verification_result",
)
