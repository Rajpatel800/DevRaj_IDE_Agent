"""
Tool registry and execution
"""
from .file_tools import (
    read_file, write_file, list_files, delete_file, FILE_TOOLS
)
from .terminal_tools import (
    run_command, install_package, TERMINAL_TOOLS
)
from .debug_tools import (
    parse_error, suggest_fix, analyze_code_quality, DEBUG_TOOLS
)


# All available tools
ALL_TOOLS = FILE_TOOLS + TERMINAL_TOOLS + DEBUG_TOOLS

# Tool execution mapping
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "delete_file": delete_file,
    "run_command": run_command,
    "install_package": install_package,
    "parse_error": parse_error,
    "suggest_fix": suggest_fix,
    "analyze_code_quality": analyze_code_quality
}


def execute_tool(tool_name: str, tool_input: dict) -> dict:
    """
    Execute a tool by name with given input
    
    Args:
        tool_name: Name of the tool to execute
        tool_input: Input parameters for the tool
        
    Returns:
        Tool execution result
    """
    if tool_name not in TOOL_FUNCTIONS:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }
    
    try:
        func = TOOL_FUNCTIONS[tool_name]
        result = func(**tool_input)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"Error executing {tool_name}: {str(e)}"
        }


__all__ = [
    'ALL_TOOLS',
    'TOOL_FUNCTIONS',
    'execute_tool',
    'FILE_TOOLS',
    'TERMINAL_TOOLS',
    'DEBUG_TOOLS'
]
