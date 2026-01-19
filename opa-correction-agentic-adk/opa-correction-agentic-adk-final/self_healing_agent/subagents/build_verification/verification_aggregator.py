from google.adk.agents import Agent
from self_healing_agent.subagents.tools import build_log_storage_tool
from self_healing_agent.subagents.shared.callbacks import rate_limit_callback
from self_healing_agent.config import config

verification_aggregator = Agent(
    name="verification_aggregator",
    model=config.llm_model,
    description="Aggregates verification results and determines overall build success",
    instruction="""You are a verification result aggregator.

    ## YOUR TASK
    
    1. **Get Results from State**:
       - terraform_valid: boolean
       - terraform_errors: list
       - opa_violations: list
       - opa_violation_count: int
       - iteration_count: int (current iteration number)
    
    2. **Determine Overall Success**:
       - build_successful = terraform_valid AND (opa_violation_count == 0)
       - CRITICAL: Both conditions must be True for success
    
    3. **Combine Errors**:
       - remaining_errors = terraform_errors + opa_violations
       - error_count = len(remaining_errors)
    
    4. **Increment Iteration**:
       - iteration_count = iteration_count + 1
    
    5. **Determine Build Status**:
       - build_status = "success" if build_successful else "failed"
    
    6. **Store Comprehensive Result in State**:
       - build_successful: boolean (True only if BOTH terraform_valid AND no OPA violations)
       - remaining_errors: list (combined errors)
       - error_count: int
       - iteration_count: int (incremented)
       - build_status: "success" | "failed"
       - build_verification_result: dict containing all above fields
    
    7. **Store Logs**:
       - Create a summary message with:
         * Terraform validation status
         * OPA evaluation status
         * Total error count
         * Iteration number
       - Call store_build_logs(log_text=summary)
    
    ## OUTPUT FORMAT
    Return final summary:
    - "Build verification SUCCESSFUL - Terraform valid ✓, OPA compliant ✓ - iteration [N]" OR
    - "Build verification FAILED - [N] errors remaining - iteration [N]"
      * Include breakdown: "[X] Terraform errors, [Y] OPA violations"
    
    ## CRITICAL
    - build_successful is True ONLY when:
      * terraform_valid = True AND
      * opa_violation_count = 0
    - This ensures loop_decision_agent has correct information
    """,
    tools=[build_log_storage_tool],
    before_model_callback=rate_limit_callback,
    output_key="verification_aggregation_result",
)
