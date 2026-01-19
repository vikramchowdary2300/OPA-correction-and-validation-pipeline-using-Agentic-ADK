"""
Shared callback functions for agents.
"""

import time
from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse


def rate_limit_callback(
    callback_context: CallbackContext, 
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Rate limit callback that waits 5 seconds before each model call.
    
    This is a before_model_callback that helps prevent hitting API rate limits
    when making many consecutive requests.
    
    Args:
        callback_context: ADK callback context with state and agent info
        llm_request: The LLM request being sent to the model
    
    Returns:
        None to continue with normal model request
    """
    agent_name = callback_context.agent_name
    
    print(f"\n{'=' * 80}")
    print(f"[Rate Limit] Agent: {agent_name}")
    print(f"[Rate Limit] Waiting 10 seconds before model call...")
    print(f"{'=' * 80}\n")
    
    time.sleep(5)
    
    print(f"[Rate Limit] Resuming execution for {agent_name}\n")
    
    # Return None to proceed with normal model request
    return None
