"""
File operations tools for reading and writing source code files.
"""

import os
from typing import Optional
from google.adk.tools import FunctionTool, ToolContext


def read_file(
    tool_context: ToolContext,
    file_path: str,
    repo_path: Optional[str] = None
) -> dict:
    """
    Read contents of a source file.
    
    Args:
        tool_context: ADK tool context
        file_path: Path to file (absolute or relative to repo_path)
        repo_path: Optional repository root path
        
    Returns:
        dict with status, content, and file_info
    """
    try:
        # Resolve full path
        if repo_path and not os.path.isabs(file_path):
            full_path = os.path.join(repo_path, file_path)
        else:
            full_path = file_path
        
        # Check if file exists
        if not os.path.exists(full_path):
            return {
                "status": "error",
                "message": f"File not found: {file_path}"
            }
        
        # Read file content
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Get file info
        file_info = {
            "size": os.path.getsize(full_path),
            "lines": len(content.splitlines()),
            "extension": os.path.splitext(file_path)[1]
        }
        
        return {
            "status": "success",
            "file_path": file_path,
            "content": content,
            "file_info": file_info,
            "message": f"Successfully read file: {file_path}"
        }
        
    except UnicodeDecodeError:
        return {
            "status": "error",
            "message": f"Failed to decode file (binary file?): {file_path}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to read file: {str(e)}",
            "error_type": type(e).__name__
        }


def write_file(
    tool_context: ToolContext,
    file_path: str,
    content: str,
    repo_path: Optional[str] = None,
    create_dirs: bool = True
) -> dict:
    """
    Write content to a source file.
    
    Args:
        tool_context: ADK tool context
        file_path: Path to file (absolute or relative to repo_path)
        content: Content to write
        repo_path: Optional repository root path
        create_dirs: Whether to create parent directories if they don't exist
        
    Returns:
        dict with status and message
    """
    try:
        # Resolve full path
        if repo_path and not os.path.isabs(file_path):
            full_path = os.path.join(repo_path, file_path)
        else:
            full_path = file_path
        
        # Create parent directories if needed
        if create_dirs:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write content
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Track modified file in state
        modified_files = tool_context.state.get("files_modified", [])
        if not isinstance(modified_files, list):
            modified_files = []
        
        if file_path not in modified_files:
            modified_files.append(file_path)
            tool_context.state["files_modified"] = modified_files
        
        return {
            "status": "success",
            "file_path": file_path,
            "bytes_written": len(content.encode('utf-8')),
            "lines_written": len(content.splitlines()),
            "message": f"Successfully wrote file: {file_path}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to write file: {str(e)}",
            "error_type": type(e).__name__
        }


def list_directory(
    tool_context: ToolContext,
    dir_path: str,
    repo_path: Optional[str] = None,
    pattern: Optional[str] = None,
    recursive: bool = False
) -> dict:
    """
    List files in a directory.
    
    Args:
        tool_context: ADK tool context
        dir_path: Directory path (absolute or relative to repo_path)
        repo_path: Optional repository root path
        pattern: Optional file pattern (e.g., "*.py")
        recursive: Whether to list recursively
        
    Returns:
        dict with status and list of files
    """
    try:
        import fnmatch
        
        # Resolve full path
        if repo_path and not os.path.isabs(dir_path):
            full_path = os.path.join(repo_path, dir_path)
        else:
            full_path = dir_path
        
        # Check if directory exists
        if not os.path.exists(full_path):
            return {
                "status": "error",
                "message": f"Directory not found: {dir_path}"
            }
        
        if not os.path.isdir(full_path):
            return {
                "status": "error",
                "message": f"Path is not a directory: {dir_path}"
            }
        
        files = []
        dirs = []
        
        if recursive:
            for root, dirnames, filenames in os.walk(full_path):
                # Filter directories (skip hidden and common non-source dirs)
                dirnames[:] = [d for d in dirnames if not d.startswith('.') 
                              and d not in ['node_modules', '__pycache__', 'venv', 'build', 'dist']]
                
                for filename in filenames:
                    if not filename.startswith('.'):
                        rel_path = os.path.relpath(os.path.join(root, filename), full_path)
                        if pattern is None or fnmatch.fnmatch(filename, pattern):
                            files.append(rel_path)
        else:
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                if os.path.isfile(item_path):
                    if not item.startswith('.'):
                        if pattern is None or fnmatch.fnmatch(item, pattern):
                            files.append(item)
                elif os.path.isdir(item_path):
                    if not item.startswith('.'):
                        dirs.append(item)
        
        return {
            "status": "success",
            "directory": dir_path,
            "files": sorted(files),
            "directories": sorted(dirs),
            "file_count": len(files),
            "message": f"Found {len(files)} files in {dir_path}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list directory: {str(e)}",
            "error_type": type(e).__name__
        }


# Create ADK tool instances
read_file_tool = FunctionTool(func=read_file)
write_file_tool = FunctionTool(func=write_file)
list_directory_tool = FunctionTool(func=list_directory)

