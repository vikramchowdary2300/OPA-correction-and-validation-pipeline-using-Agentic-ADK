"""
Build operations tools for detecting build systems and running builds.
"""

import os
import subprocess
import json
from typing import Optional
from google.adk.tools import FunctionTool, ToolContext


def detect_build_system(
    tool_context: ToolContext,
    repo_path: str
) -> dict:
    """
    Detect the build system used in a repository.
    
    Args:
        tool_context: ADK tool context
        repo_path: Path to repository
        
    Returns:
        dict with status, build_system, and build_command
    """
    try:
        build_systems = []
        
        # Check for various build system indicators
        indicators = {
            "npm": ["package.json"],
            "yarn": ["yarn.lock"],
            "maven": ["pom.xml"],
            "gradle": ["build.gradle", "build.gradle.kts"],
            "make": ["Makefile"],
            "cmake": ["CMakeLists.txt"],
            "cargo": ["Cargo.toml"],
            "go": ["go.mod"],
            "python": ["setup.py", "pyproject.toml", "requirements.txt"],
        }
        
        build_commands = {
            "npm": "npm run build",
            "yarn": "yarn build",
            "maven": "mvn clean install",
            "gradle": "./gradlew build",
            "make": "make",
            "cmake": "cmake --build .",
            "cargo": "cargo build",
            "go": "go build ./...",
            "python": "python setup.py build",
        }
        
        # Check which build system files exist
        for system, files in indicators.items():
            for file in files:
                if os.path.exists(os.path.join(repo_path, file)):
                    build_systems.append(system)
                    break
        
        if not build_systems:
            return {
                "status": "error",
                "message": "No recognized build system found"
            }
        
        # Use the first detected build system
        primary_system = build_systems[0]
        command = build_commands.get(primary_system, "")
        
        # Store in state
        tool_context.state["build_system"] = primary_system
        tool_context.state["build_command"] = command
        
        return {
            "status": "success",
            "build_system": primary_system,
            "all_detected": build_systems,
            "build_command": command,
            "message": f"Detected build system: {primary_system}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to detect build system: {str(e)}",
            "error_type": type(e).__name__
        }


def run_build(
    tool_context: ToolContext,
    repo_path: str,
    command: Optional[str] = None,
    timeout: int = 300
) -> dict:
    """
    Run build command and capture output.
    
    Args:
        tool_context: ADK tool context
        repo_path: Path to repository
        command: Optional build command (auto-detected if not provided)
        timeout: Command timeout in seconds (default: 300)
        
    Returns:
        dict with status, output, and success flag
    """
    try:
        # Use provided command or get from state
        if command is None:
            command = tool_context.state.get("build_command")
        
        if not command:
            return {
                "status": "error",
                "message": "No build command provided or detected"
            }
        
        # Split command into parts
        cmd_parts = command.split()
        
        # Run build command
        result = subprocess.run(
            cmd_parts,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Combine stdout and stderr
        output = result.stdout + "\n" + result.stderr
        
        # Determine if build was successful
        build_successful = result.returncode == 0
        
        # Store results in state
        tool_context.state["latest_build_output"] = output
        tool_context.state["build_successful"] = build_successful
        tool_context.state["build_return_code"] = result.returncode
        
        return {
            "status": "success",
            "build_successful": build_successful,
            "return_code": result.returncode,
            "output": output,
            "output_length": len(output),
            "message": f"Build {'succeeded' if build_successful else 'failed'}"
        }
        
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": f"Build command timed out after {timeout} seconds"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to run build: {str(e)}",
            "error_type": type(e).__name__
        }


def install_dependency(
    tool_context: ToolContext,
    repo_path: str,
    dependency: str,
    build_system: Optional[str] = None
) -> dict:
    """
    Install a missing dependency.
    
    Args:
        tool_context: ADK tool context
        repo_path: Path to repository
        dependency: Dependency name/identifier
        build_system: Optional build system (auto-detected if not provided)
        
    Returns:
        dict with status and message
    """
    try:
        # Use provided build system or get from state
        if build_system is None:
            build_system = tool_context.state.get("build_system")
        
        if not build_system:
            return {
                "status": "error",
                "message": "No build system provided or detected"
            }
        
        # Determine install command based on build system
        install_commands = {
            "npm": ["npm", "install", dependency, "--save"],
            "yarn": ["yarn", "add", dependency],
            "maven": None,  # Maven dependencies are added to pom.xml
            "gradle": None,  # Gradle dependencies are added to build.gradle
            "pip": ["pip", "install", dependency],
            "cargo": ["cargo", "add", dependency],
            "go": ["go", "get", dependency],
        }
        
        cmd = install_commands.get(build_system)
        
        if cmd is None:
            return {
                "status": "error",
                "message": f"Automatic dependency installation not supported for {build_system}. "
                          f"Dependencies must be added to config file manually."
            }
        
        # Run install command
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            return {
                "status": "success",
                "dependency": dependency,
                "build_system": build_system,
                "output": result.stdout,
                "message": f"Successfully installed dependency: {dependency}"
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to install dependency: {result.stderr}",
                "error_details": result.stderr
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to install dependency: {str(e)}",
            "error_type": type(e).__name__
        }


def parse_build_output(
    tool_context: ToolContext,
    build_output: str
) -> dict:
    """
    Parse build output to extract error information.
    
    Args:
        tool_context: ADK tool context
        build_output: Build output text
        
    Returns:
        dict with parsed errors and warnings
    """
    try:
        errors = []
        warnings = []
        
        lines = build_output.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Common error patterns
            if any(keyword in line_lower for keyword in ['error:', 'error ', 'failed:', 'exception:']):
                error_info = {
                    "line_number": i + 1,
                    "message": line.strip(),
                    "context": '\n'.join(lines[max(0, i-2):min(len(lines), i+3)])
                }
                
                # Try to extract file path
                for part in line.split():
                    if '/' in part or '\\' in part:
                        if any(ext in part for ext in ['.java', '.js', '.py', '.cpp', '.go', '.ts']):
                            error_info["file"] = part
                            break
                
                errors.append(error_info)
            
            # Common warning patterns
            elif any(keyword in line_lower for keyword in ['warning:', 'warn:']):
                warnings.append({
                    "line_number": i + 1,
                    "message": line.strip()
                })
        
        # Store in state
        tool_context.state["parsed_errors"] = errors
        tool_context.state["parsed_warnings"] = warnings
        
        return {
            "status": "success",
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings,
            "message": f"Found {len(errors)} errors and {len(warnings)} warnings"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to parse build output: {str(e)}",
            "error_type": type(e).__name__
        }


# NOTE: All build operation tools have been removed as they are not needed for Terraform/OPA workflows.
# This file is kept for potential future use but currently exports no tools.
