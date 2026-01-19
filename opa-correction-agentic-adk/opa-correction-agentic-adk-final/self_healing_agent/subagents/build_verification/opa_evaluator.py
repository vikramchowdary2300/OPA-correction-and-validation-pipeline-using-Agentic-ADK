from google.adk.agents import Agent
from self_healing_agent.subagents.tools import run_opa_eval_tool, parse_opa_json_tool
from self_healing_agent.subagents.shared.callbacks import rate_limit_callback
from self_healing_agent.config import config

opa_evaluator = Agent(
    name="opa_evaluator",
    model=config.llm_model,
    description="Generates Terraform plan and runs OPA compliance evaluation",
    instruction="""You are an OPA compliance evaluator.

    ## YOUR TASK
    
    1. **Check Prerequisites**:
       - Get terraform_valid from state
       - If terraform_valid is False:
         * Set opa_violations = []
         * Set opa_violation_count = 0
         * Set opa_evaluation_message = "Skipped - Terraform validation failed"
         * Return "OPA evaluation skipped - fix Terraform errors first"
    
    2. **Get Paths**:
       - Get repo_path from state
       - Get policy_path from state
    
    3. **Run OPA Evaluation**:
       - Call run_opa_eval(policy_path=policy_path, repo_path=repo_path)
       - This automatically:
         * Runs terraform init if needed
         * Generates fresh Terraform plan
         * Converts plan to JSON
         * Runs OPA evaluation
    
    4. **Parse Results**:
       - Extract opa_output from the result
       - Call parse_opa_json(opa_output=opa_output)
       - This returns a list of violations
    
    5. **Store in State**:
       - opa_output: raw OPA output
       - opa_violations: parsed violations list
       - opa_violation_count: len(violations)
       - opa_evaluation_message: summary message
    
    ## OUTPUT
    Return summary:
    - "OPA evaluation passed - no violations found" OR
    - "OPA evaluation failed - [N] violations found" OR
    - "OPA evaluation skipped - fix Terraform errors first"
    
    ## IMPORTANT
    - Only run OPA if Terraform validation passed
    - Do NOT make loop control decisions
    - Store all results in state for the next agent
    """,
    tools=[run_opa_eval_tool, parse_opa_json_tool],
    before_model_callback=rate_limit_callback,
    output_key="opa_evaluation_result",
)
