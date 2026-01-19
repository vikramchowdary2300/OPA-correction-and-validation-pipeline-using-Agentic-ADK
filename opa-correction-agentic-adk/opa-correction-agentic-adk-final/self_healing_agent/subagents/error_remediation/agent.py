from google.adk.agents import Agent
from self_healing_agent.subagents.tools import (
    read_file_tool,
    write_file_tool,
    list_directory_tool
)
from self_healing_agent.subagents.shared.callbacks import rate_limit_callback


from self_healing_agent.config import config

error_remediation = Agent(
    name="error_remediation",
    model=config.llm_model,
    description="Fixes identified build errors by modifying source code, updating dependencies, and correcting configurations.",
    instruction="""You are an expert Terraform engineer specializing in OPA compliance remediation.
    
    ## YOUR AVAILABLE TOOLS
    1. read_file(file_path, repo_path) - Read source file content
    2. write_file(file_path, content, repo_path, create_dirs) - Write/update source file
    3. list_directory(dir_path, repo_path, pattern, recursive) - List files
    
    ## YOUR TASK
    
    Fix ALL OPA violations from the state (errors list).
    Get repo_path from state.
    
    For each error:
    
    1. **Read the problematic file**:
       - Use read_file tool.
       - If file path is "unknown", use list_directory to find relevant .tf files.
    
    2. **Analyze the Violation**:
       - Message: e.g., "Instance type must be t2.micro"
       - Resource: e.g., "aws_instance.web"
    
    3. **Apply the Fix**:
       - Locate the resource in the HCL code.
       - Modify the attribute to satisfy the policy.
       - Examples:
         * **Instance Type**: Change `instance_type = "..."` to allowed value.
         * **Tags**: Add `tags = { ... }` block or add missing tags.
         * **Encryption**: Set `encrypted = true` or `sse_algorithm = "AES256"`.
         * **CIDR**: Change `cidr_block` to private range.
    
    4. **Write the fixed code**:
       - Use write_file tool with the complete fixed content.
    
    5. **Output summary**:
       - File path
       - Violation fixed
       - Change description
    
    ## IMPORTANT
    - Preserve existing comments and structure where possible.
    - If multiple resources need fixing, fix all of them.
    - Do not delete required attributes.
    """,
    tools=[
        read_file_tool,
        write_file_tool,
        list_directory_tool
    ],
    before_model_callback=rate_limit_callback,
    output_key="fixes_applied",
)

