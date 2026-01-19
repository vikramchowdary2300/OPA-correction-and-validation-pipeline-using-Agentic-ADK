"""
Main orchestration agent with loop logic for self-healing workflow using ADK's LoopAgent.

Pattern based on ADK best practices:
- Root agent is SequentialAgent
- LoopAgent is used as a sub-agent within the sequential flow
- Loop exits when exit_loop tool sets tool_context.actions.escalate = True
"""

from google.adk.agents import Agent, SequentialAgent, LoopAgent
from .config import config, get_max_iterations
from google.adk.apps import App, ResumabilityConfig
from .subagents.log_analyzer import log_analyzer
from .subagents.repository_setup import repository_setup
from .subagents.error_remediation import error_remediation
from .subagents.build_verification import build_verification
from .subagents.code_finalizer import code_finalizer
from .subagents.tools.loop_control import exit_loop_tool
from .subagents.shared.callbacks import rate_limit_callback
from .subagents.syntax_verifier.agent import syntax_verifier
import agentops
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

print("application started")
# Initialize AgentOps for observability
# Must be called before creating ADK App to capture all agent activity
agentops.init(
    api_key=os.getenv("AGENTOPS_API_KEY"),
    trace_name="self-healing-adk-workflow"
)

# Loop decision agent - decides whether to exit the loop
loop_decision_agent = Agent(
    name="loop_decision",
    model=config.llm_model,
    description="Decides whether to continue the fix loop or exit based on verification results.",
    instruction="""You are a decision agent controlling the fix loop.
    
    ## INPUT
    - You will receive the output from the build_verification agent.
    - The build_verification_result in state contains:
      * build_successful: boolean (True ONLY if terraform_valid=True AND opa_violation_count=0)
      * remaining_errors: list (combined terraform + opa errors)
      * error_count: int
      * iteration_count: int
      * build_status: "success" | "failed"
    
    ## YOUR TASK
    1. Get build_verification_result from state
    2. Check build_successful field:
       - If build_successful is True:
         * This means BOTH Terraform syntax is valid AND OPA evaluation passed
         * Call exit_loop_tool("Build successful - Terraform valid ✓, OPA compliant ✓")
       - If build_successful is False:
         * Return "continue" to proceed to next iteration
    
    ## CRITICAL RULES
    - ONLY call exit_loop_tool when build_successful is True
    - build_successful is True ONLY when:
      * Terraform validation passed (terraform_valid = True) AND
      * OPA evaluation passed (opa_violation_count = 0)
    - Do NOT exit based on syntax_verifier output
    - Do NOT exit based on error_remediation output
    - ONLY exit based on build_verification_result.build_successful
    - If there are remaining_errors, you MUST return "continue"
    
    ## OUTPUT
    - Call exit_loop_tool(reason) to stop the loop when BOTH conditions are met.
    - Return "continue" to keep iterating when either condition fails.
    """,
    tools=[exit_loop_tool],
    before_model_callback=rate_limit_callback,
    output_key="loop_decision",
)

# Create the fix loop using LoopAgent
# Following ADK pattern: LoopAgent contains sub_agents that execute in sequence
# Loop exits when exit_loop tool is called (sets escalate=True) or max_iterations reached
fix_loop = LoopAgent(
    name="fix_loop",
    description="Iteratively fixes errors and verifies build until success or max iterations",
    sub_agents=[
        error_remediation,      # Step 1: Fix the errors
        syntax_verifier,        # Step 2: Verify syntax and fix invalid resource types
        build_verification,     # Step 3: Rebuild and verify
        loop_decision_agent,    # Step 4: Check if we should exit
    ],
    max_iterations=get_max_iterations() * 2,  # Configurable from .env (doubled for safety)
)


# Root agent is SequentialAgent (following ADK best practice)
# LoopAgent is used as a sub-agent within the sequential workflow
root_agent = SequentialAgent(
    name="self_healing_workflow",
    sub_agents=[
        log_analyzer,        # Step 1: Analyze logs and identify errors
        repository_setup,    # Step 2: Clone repo and setup environment
        fix_loop,            # Step 3: Loop: fix → verify → check (LoopAgent)
        code_finalizer,      # Step 4: Commit changes and create PR
    ],
    description="Self-healing workflow: Analyze → Setup → Loop(Fix+Verify+Check) → Finalize",
)

# Create the ADK App with the self-healing workflow as root agent
app = App(
    name="self_healing_agent",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(
        is_resumable=True,
    ),
)