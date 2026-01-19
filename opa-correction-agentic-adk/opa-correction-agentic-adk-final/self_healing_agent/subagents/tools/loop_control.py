"""
Loop control tools for managing the fix loop.
"""

from typing import Dict, Any
from google.adk.tools import FunctionTool, ToolContext


def exit_loop(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Exit the fix loop when build is successful or max iterations reached.
    
    This tool should be called by the loop decision agent when:
    - Build is successful (build_successful = True)
    - Max iterations reached
    - No more errors to fix
    
    Args:
        tool_context: Tool execution context
        
    Returns:
        Empty dictionary
    """
    print("\n----------- EXIT LOOP TRIGGERED -----------")
    print("Exiting the error fixing loop")
    print("Reason: Build successful or termination condition met")
    print("------------------------------------------\n")
    
    # Signal to LoopAgent to stop iterating
    tool_context.actions.escalate = True
    
    return {
        "status": "loop_exited",
        "message": "Fix loop terminated"
    }


# Create the tool instance
exit_loop_tool = FunctionTool(func=exit_loop)

