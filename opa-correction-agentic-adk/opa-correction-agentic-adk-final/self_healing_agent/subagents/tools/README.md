# ADK Tools

This directory contains custom ADK tools for the self-healing agent.

## Build Log Storage Tool

### Overview

The `build_log_storage_tool` is an ADK tool that processes log text and stores only build-related logs to the ADK state.

### Features

- **Log Filtering**: Automatically identifies build-related logs using keywords
- **State Management**: Stores filtered logs in ADK state for persistence
- **Incremental Storage**: Appends new build logs to existing ones in state
- **Comprehensive Keywords**: Recognizes multiple build systems and tools

### Build Keywords Detected

The tool identifies logs containing the following keywords:
- `build`, `building`, `built`
- `compile`, `compiling`, `compilation`
- `make`, `cmake`
- `gradle`, `maven`
- `npm`, `yarn`
- `webpack`, `bundling`
- `linking`, `assembling`

### Usage

#### 1. Import the Tool

```python
from self_healing_agent.subagents.tools import build_log_storage_tool
```

#### 2. Add to Agent

```python
from google.adk.agents import Agent
from self_healing_agent.subagents.tools import build_log_storage_tool

agent = Agent(
    name="my_agent",
    model="gemini-2.5-flash",
    description="Agent with build log storage capability",
    instruction="Process logs and store build information",
    tools=[build_log_storage_tool],
)
```

#### 3. Use in Agent Flow

The agent can now call the `store_build_logs` function with log text:

```python
# Example log text
log_text = """
[INFO] Starting application
[INFO] Building project...
[INFO] Compiling source files
[ERROR] Build failed: missing dependency
[INFO] Server started
"""

# The agent will process this and store build-related lines
# Result will include status and count of stored logs
```

### Return Format

The tool returns a dictionary with the following structure:

```python
{
    "status": "success",  # or "error"
    "message": "Build logs processed and stored successfully",
    "build_logs_count": 3,  # Number of new build logs found
    "total_logs_in_state": 10  # Total build logs in state
}
```

### State Access

Build logs are stored in the ADK state under the key `build_logs`:

```python
# Access stored build logs from state
build_logs = tool_context.state.get("build_logs", [])
```

### Example Integration

```python
from google.adk.agents import Agent
from self_healing_agent.subagents.tools import build_log_storage_tool

log_processor = Agent(
    name="log_processor",
    model="gemini-2.5-flash",
    description="Processes logs and extracts build information",
    instruction="""
    You are a log processor that extracts build-related information.
    Use the store_build_logs tool to analyze and store build logs.
    """,
    tools=[build_log_storage_tool],
    output_key="build_summary",
)
```

