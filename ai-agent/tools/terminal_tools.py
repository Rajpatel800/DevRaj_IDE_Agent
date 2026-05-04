"""
Terminal command execution tools
"""
import subprocess
import shlex
from typing import Dict, Any
from config import COMMAND_TIMEOUT


def run_command(cmd: str, timeout: int = COMMAND_TIMEOUT) -> Dict[str, Any]:
    """
    Execute a shell command
    
    Args:
        cmd: Command to execute
        timeout: Timeout in seconds
        
    Returns:
        Dict with success status, stdout, stderr, and return code
    """
    try:
        # Use shell=True for complex commands, but be aware of security implications
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "command": cmd
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds",
            "command": cmd
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error executing command: {str(e)}",
            "command": cmd
        }


def install_package(package_name: str, package_manager: str = "pip") -> Dict[str, Any]:
    """
    Install a package using specified package manager
    
    Args:
        package_name: Name of the package to install
        package_manager: Package manager to use (pip, npm, etc.)
        
    Returns:
        Dict with installation result
    """
    commands = {
        "pip": f"pip install {package_name}",
        "npm": f"npm install {package_name}",
        "yarn": f"yarn add {package_name}",
        "apt": f"sudo apt-get install -y {package_name}"
    }
    
    if package_manager not in commands:
        return {
            "success": False,
            "error": f"Unsupported package manager: {package_manager}"
        }
    
    cmd = commands[package_manager]
    result = run_command(cmd, timeout=120)  # Longer timeout for installations
    
    return {
        **result,
        "package": package_name,
        "package_manager": package_manager
    }


# Tool definitions for Claude
TERMINAL_TOOLS = [
    {
        "name": "run_command",
        "description": "Execute a shell command and return the output",
        "input_schema": {
            "type": "object",
            "properties": {
                "cmd": {
                    "type": "string",
                    "description": "The shell command to execute"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 30)"
                }
            },
            "required": ["cmd"]
        }
    },
    {
        "name": "install_package",
        "description": "Install a package using a package manager (pip, npm, yarn, apt)",
        "input_schema": {
            "type": "object",
            "properties": {
                "package_name": {
                    "type": "string",
                    "description": "Name of the package to install"
                },
                "package_manager": {
                    "type": "string",
                    "description": "Package manager to use (pip, npm, yarn, apt)",
                    "enum": ["pip", "npm", "yarn", "apt"]
                }
            },
            "required": ["package_name"]
        }
    }
]
