"""
File manipulation tools
"""
import os
from pathlib import Path
from typing import Dict, Any, List


def read_file(path: str) -> Dict[str, Any]:
    """
    Read contents of a file
    
    Args:
        path: Path to the file
        
    Returns:
        Dict with success status and content or error
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {
            "success": True,
            "content": content,
            "message": f"Successfully read {path}"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"File not found: {path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error reading file: {str(e)}"
        }


def write_file(path: str, content: str) -> Dict[str, Any]:
    """
    Write content to a file (creates directories if needed)
    
    Args:
        path: Path to the file
        content: Content to write
        
    Returns:
        Dict with success status and message
    """
    try:
        # Create parent directories if they don't exist
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "message": f"Successfully wrote to {path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error writing file: {str(e)}"
        }


def list_files(directory: str = ".") -> Dict[str, Any]:
    """
    List files and directories in a path
    
    Args:
        directory: Directory path to list
        
    Returns:
        Dict with success status and list of files/dirs
    """
    try:
        items = []
        for item in os.listdir(directory):
            full_path = os.path.join(directory, item)
            items.append({
                "name": item,
                "type": "directory" if os.path.isdir(full_path) else "file",
                "path": full_path
            })
        
        return {
            "success": True,
            "items": items,
            "count": len(items)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error listing directory: {str(e)}"
        }


def delete_file(path: str) -> Dict[str, Any]:
    """
    Delete a file
    
    Args:
        path: Path to the file
        
    Returns:
        Dict with success status
    """
    try:
        os.remove(path)
        return {
            "success": True,
            "message": f"Successfully deleted {path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error deleting file: {str(e)}"
        }


# Tool definitions for Claude
FILE_TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Creates parent directories if needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "list_files",
        "description": "List files and directories in a given path",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to list (defaults to current directory)"
                }
            },
            "required": []
        }
    },
    {
        "name": "delete_file",
        "description": "Delete a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to delete"
                }
            },
            "required": ["path"]
        }
    }
]
