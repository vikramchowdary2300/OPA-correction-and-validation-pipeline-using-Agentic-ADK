from google.adk.agents import Agent
from self_healing_agent.subagents.tools import validate_terraform_tool
from self_healing_agent.subagents.shared.callbacks import rate_limit_callback
from self_healing_agent.config import config

terraform_validator = Agent(
    name="terraform_validator",
    model=config.llm_model,
    description="Validates Terraform syntax and schema",
    instruction="""You are a Terraform syntax validator.

    ## YOUR TASK
    1. Get repo_path from state
    2. Call validate_terraform(path=repo_path)
    3. Analyze the result:
       - If successful (success=True): Terraform syntax is valid
       - If failed (success=False): Extract error details from output
    
    4. Store results in state:
       - terraform_valid: True if validation passed, False otherwise
       - terraform_errors: List of error messages (empty if valid)
       - terraform_validation_message: Summary message
    
    ## OUTPUT
    Return a brief summary:
    - "Terraform validation passed - syntax is correct" OR
    - "Terraform validation failed - [N] errors found"
    
    ## IMPORTANT
    - Do NOT proceed to OPA evaluation - that's the next agent's job
    - Do NOT make loop control decisions
    - Simply validate syntax and store results in state
    """,
    tools=[validate_terraform_tool],
    before_model_callback=rate_limit_callback,
    output_key="terraform_validation_result",
)
