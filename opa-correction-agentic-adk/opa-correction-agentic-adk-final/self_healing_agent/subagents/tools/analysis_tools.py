"""
Analysis tools for parsing and understanding logs and errors.
"""

import re
from typing import Optional
from google.adk.tools import FunctionTool, ToolContext


def parse_error_details(
    tool_context: ToolContext,
    error_text: str
) -> dict:
    """
    Parse error text to extract structured information.
    
    Args:
        tool_context: ADK tool context
        error_text: Error message text
        
    Returns:
        dict with extracted error details
    """
    try:
        # Initialize error details
        error_details = {
            "raw_text": error_text,
            "error_type": "unknown",
            "file_path": None,
            "line_number": None,
            "column_number": None,
            "error_message": error_text,
            "severity": "medium"
        }
        
        # Extract file path and line number (common pattern: file.ext:line:col)
        file_pattern = r'([/\w\-\.]+\.(?:java|js|ts|py|cpp|go|rs|rb|php|cs|kt))[:(\s](\d+)(?::(\d+))?'
        file_match = re.search(file_pattern, error_text)
        
        if file_match:
            error_details["file_path"] = file_match.group(1)
            error_details["line_number"] = int(file_match.group(2))
            if file_match.group(3):
                error_details["column_number"] = int(file_match.group(3))
        
        # Categorize error type
        error_text_lower = error_text.lower()
        
        if any(keyword in error_text_lower for keyword in ['syntaxerror', 'syntax error', 'unexpected token']):
            error_details["error_type"] = "syntax"
            error_details["severity"] = "high"
        elif any(keyword in error_text_lower for keyword in ['cannot find', 'not found', 'undefined', 'unresolved']):
            error_details["error_type"] = "reference"
            error_details["severity"] = "high"
        elif any(keyword in error_text_lower for keyword in ['type error', 'type mismatch', 'incompatible']):
            error_details["error_type"] = "type"
            error_details["severity"] = "medium"
        elif any(keyword in error_text_lower for keyword in ['import', 'module', 'package']):
            error_details["error_type"] = "import"
            error_details["severity"] = "high"
        elif any(keyword in error_text_lower for keyword in ['nullpointer', 'null reference', 'nullptr']):
            error_details["error_type"] = "null_reference"
            error_details["severity"] = "critical"
        elif any(keyword in error_text_lower for keyword in ['dependency', 'missing package']):
            error_details["error_type"] = "dependency"
            error_details["severity"] = "high"
        elif any(keyword in error_text_lower for keyword in ['compilation', 'compile']):
            error_details["error_type"] = "compilation"
            error_details["severity"] = "high"
        
        return {
            "status": "success",
            "error_details": error_details,
            "message": f"Parsed {error_details['error_type']} error"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to parse error details: {str(e)}",
            "error_type": type(e).__name__
        }


def extract_stack_trace(
    tool_context: ToolContext,
    log_section: str
) -> dict:
    """
    Extract stack trace from log section.
    
    Args:
        tool_context: ADK tool context
        log_section: Log section containing potential stack trace
        
    Returns:
        dict with extracted stack trace
    """
    try:
        lines = log_section.split('\n')
        stack_trace = []
        in_stack = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Detect start of stack trace
            if any(keyword in line_stripped.lower() for keyword in 
                   ['traceback', 'stack trace:', 'exception', 'error:']):
                in_stack = True
                stack_trace.append(line_stripped)
                continue
            
            # Common stack trace patterns
            if in_stack:
                # Java/Kotlin: "at package.Class.method(File.java:123)"
                # Python: "File "file.py", line 123, in function"
                # JavaScript: "at function (file.js:123:45)"
                if (line_stripped.startswith('at ') or 
                    'File "' in line_stripped or
                    line_stripped.startswith('  ') or
                    re.match(r'^\s+\w+', line)):
                    stack_trace.append(line_stripped)
                elif line_stripped and not line_stripped[0].isspace():
                    # Stack trace ended
                    break
        
        if stack_trace:
            return {
                "status": "success",
                "stack_trace": stack_trace,
                "frame_count": len(stack_trace),
                "message": f"Extracted stack trace with {len(stack_trace)} frames"
            }
        else:
            return {
                "status": "success",
                "stack_trace": [],
                "frame_count": 0,
                "message": "No stack trace found"
            }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to extract stack trace: {str(e)}",
            "error_type": type(e).__name__
        }


def extract_file_info(
    tool_context: ToolContext,
    error_message: str
) -> dict:
    """
    Extract file path and location information from error message.
    
    Args:
        tool_context: ADK tool context
        error_message: Error message containing file information
        
    Returns:
        dict with extracted file information
    """
    try:
        # Multiple patterns for different error formats
        patterns = [
            # Pattern 1: file.ext:line:col
            r'([/\w\-\.]+\.(?:java|js|ts|py|cpp|go|rs|rb|php|cs|kt|tsx|jsx)):(\d+):(\d+)',
            # Pattern 2: file.ext:line
            r'([/\w\-\.]+\.(?:java|js|ts|py|cpp|go|rs|rb|php|cs|kt|tsx|jsx)):(\d+)',
            # Pattern 3: "file.ext", line line_num
            r'"([/\w\-\.]+\.(?:java|js|ts|py|cpp|go|rs|rb|php|cs|kt|tsx|jsx))",\s+line\s+(\d+)',
            # Pattern 4: at file.ext:line:col
            r'at\s+([/\w\-\.]+\.(?:java|js|ts|py|cpp|go|rs|rb|php|cs|kt|tsx|jsx)):(\d+):(\d+)',
            # Pattern 5: (file.ext:line)
            r'\(([/\w\-\.]+\.(?:java|js|ts|py|cpp|go|rs|rb|php|cs|kt|tsx|jsx)):(\d+)\)',
        ]
        
        file_info = {
            "file_path": None,
            "line_number": None,
            "column_number": None,
            "found": False
        }
        
        for pattern in patterns:
            match = re.search(pattern, error_message)
            if match:
                file_info["file_path"] = match.group(1)
                file_info["line_number"] = int(match.group(2))
                if len(match.groups()) >= 3 and match.group(3):
                    file_info["column_number"] = int(match.group(3))
                file_info["found"] = True
                break
        
        return {
            "status": "success",
            "file_info": file_info,
            "message": f"{'Found' if file_info['found'] else 'Did not find'} file information"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to extract file info: {str(e)}",
            "error_type": type(e).__name__
        }


def categorize_error_type(
    tool_context: ToolContext,
    error_text: str
) -> dict:
    """
    Categorize the type of error for prioritization.
    
    Args:
        tool_context: ADK tool context
        error_text: Error message text
        
    Returns:
        dict with error category and fixability assessment
    """
    try:
        error_text_lower = error_text.lower()
        
        categories = {
            "syntax": {
                "keywords": ['syntax error', 'unexpected token', 'unexpected end', 'parsing error'],
                "fixable": True,
                "priority": "high"
            },
            "import": {
                "keywords": ['cannot find module', 'import error', 'module not found', 'no module named'],
                "fixable": True,
                "priority": "high"
            },
            "dependency": {
                "keywords": ['missing dependency', 'package not found', 'could not resolve dependency'],
                "fixable": True,
                "priority": "high"
            },
            "type": {
                "keywords": ['type error', 'type mismatch', 'incompatible types'],
                "fixable": True,
                "priority": "medium"
            },
            "reference": {
                "keywords": ['undefined reference', 'cannot find symbol', 'undeclared identifier'],
                "fixable": True,
                "priority": "high"
            },
            "null_pointer": {
                "keywords": ['nullpointerexception', 'null reference', 'nullptr'],
                "fixable": True,
                "priority": "high"
            },
            "runtime": {
                "keywords": ['runtime error', 'execution error'],
                "fixable": False,
                "priority": "low"
            },
            "configuration": {
                "keywords": ['configuration error', 'config error', 'invalid configuration'],
                "fixable": True,
                "priority": "medium"
            }
        }
        
        detected_category = "unknown"
        fixable = False
        priority = "low"
        
        for category, info in categories.items():
            if any(keyword in error_text_lower for keyword in info["keywords"]):
                detected_category = category
                fixable = info["fixable"]
                priority = info["priority"]
                break
        
        return {
            "status": "success",
            "category": detected_category,
            "fixable": fixable,
            "priority": priority,
            "message": f"Categorized as {detected_category} error (fixable: {fixable})"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to categorize error: {str(e)}",
            "error_type": type(e).__name__
        }


# Create ADK tool instances
parse_error_details_tool = FunctionTool(func=parse_error_details)

# NOTE: The following tools have been removed as they are not used by any agents:
# - extract_stack_trace_tool (OPA errors don't have stack traces)
# - extract_file_info_tool (not used)
# - categorize_error_type_tool (not used)


