"""
Debugging and error analysis tools
"""
import re
from typing import Dict, Any, List


def parse_error(log: str) -> Dict[str, Any]:
    """
    Parse error messages from logs
    
    Args:
        log: Error log or stack trace
        
    Returns:
        Dict with parsed error information
    """
    errors = []
    
    # Common error patterns
    patterns = {
        "python": r"(.*Error|.*Exception): (.+)",
        "javascript": r"(Error|TypeError|ReferenceError): (.+)",
        "traceback": r"File \"(.+)\", line (\d+)",
        "module_not_found": r"ModuleNotFoundError: No module named '(.+)'",
        "import_error": r"ImportError: (.+)",
        "syntax_error": r"SyntaxError: (.+)"
    }
    
    for error_type, pattern in patterns.items():
        matches = re.finditer(pattern, log, re.MULTILINE)
        for match in matches:
            errors.append({
                "type": error_type,
                "match": match.group(0),
                "groups": match.groups()
            })
    
    # Extract file paths and line numbers
    file_references = re.findall(r'File "(.+)", line (\d+)', log)
    
    return {
        "success": True,
        "errors": errors,
        "file_references": [
            {"file": f, "line": int(l)} for f, l in file_references
        ],
        "raw_log": log[:500]  # First 500 chars
    }


def suggest_fix(error_type: str, error_message: str) -> Dict[str, Any]:
    """
    Suggest fixes for common errors
    
    Args:
        error_type: Type of error
        error_message: Error message
        
    Returns:
        Dict with suggested fixes
    """
    suggestions = {
        "ModuleNotFoundError": [
            "Install the missing module using pip install <module_name>",
            "Check if the module name is spelled correctly",
            "Verify the module is in your requirements.txt"
        ],
        "ImportError": [
            "Check if the import path is correct",
            "Verify the module is installed",
            "Check for circular imports"
        ],
        "SyntaxError": [
            "Check for missing colons, parentheses, or brackets",
            "Verify indentation is consistent",
            "Look for unclosed strings or comments"
        ],
        "TypeError": [
            "Check function arguments and types",
            "Verify object methods exist",
            "Check for None values"
        ],
        "FileNotFoundError": [
            "Verify the file path is correct",
            "Check if the file exists",
            "Use absolute paths or check working directory"
        ]
    }
    
    # Find matching suggestions
    matched_suggestions = []
    for key, fixes in suggestions.items():
        if key.lower() in error_type.lower() or key.lower() in error_message.lower():
            matched_suggestions.extend(fixes)
    
    if not matched_suggestions:
        matched_suggestions = ["Review the error message and stack trace carefully"]
    
    return {
        "success": True,
        "error_type": error_type,
        "suggestions": matched_suggestions
    }


def analyze_code_quality(code: str) -> Dict[str, Any]:
    """
    Basic code quality analysis
    
    Args:
        code: Source code to analyze
        
    Returns:
        Dict with quality metrics and suggestions
    """
    issues = []
    
    # Check for common issues
    if "print(" in code:
        issues.append("Consider using logging instead of print statements")
    
    if "except:" in code or "except Exception:" in code:
        issues.append("Avoid bare except clauses; catch specific exceptions")
    
    if len(code.split('\n')) > 100:
        issues.append("Function/file is long; consider breaking into smaller pieces")
    
    # Count lines
    lines = code.split('\n')
    blank_lines = sum(1 for line in lines if not line.strip())
    comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
    
    return {
        "success": True,
        "total_lines": len(lines),
        "blank_lines": blank_lines,
        "comment_lines": comment_lines,
        "code_lines": len(lines) - blank_lines - comment_lines,
        "issues": issues
    }


# Tool definitions for Claude
DEBUG_TOOLS = [
    {
        "name": "parse_error",
        "description": "Parse error messages and stack traces to extract useful information",
        "input_schema": {
            "type": "object",
            "properties": {
                "log": {
                    "type": "string",
                    "description": "Error log or stack trace to parse"
                }
            },
            "required": ["log"]
        }
    },
    {
        "name": "suggest_fix",
        "description": "Get suggestions for fixing common errors",
        "input_schema": {
            "type": "object",
            "properties": {
                "error_type": {
                    "type": "string",
                    "description": "Type of error (e.g., ModuleNotFoundError, SyntaxError)"
                },
                "error_message": {
                    "type": "string",
                    "description": "The error message"
                }
            },
            "required": ["error_type", "error_message"]
        }
    },
    {
        "name": "analyze_code_quality",
        "description": "Analyze code quality and provide suggestions",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Source code to analyze"
                }
            },
            "required": ["code"]
        }
    }
]
