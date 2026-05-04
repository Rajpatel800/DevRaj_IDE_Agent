"""
Memory management for conversation history
"""
from typing import List, Dict, Any


class Memory:
    """Manages conversation history and context"""
    
    def __init__(self, max_history: int = 50):
        self.messages: List[Dict[str, str]] = []
        self.max_history = max_history
        self.context: Dict[str, Any] = {}
    
    def add_user_message(self, content: str):
        """Add a user message to history"""
        self.messages.append({
            "role": "user",
            "content": content
        })
        self._trim_history()
    
    def add_assistant_message(self, content: str):
        """Add an assistant message to history"""
        self.messages.append({
            "role": "assistant",
            "content": content
        })
        self._trim_history()
    
    def add_tool_result(self, tool_use_id: str, result: str):
        """Add tool result to conversation"""
        self.messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": result
                }
            ]
        })
        self._trim_history()
    
    def add_tool_use(self, tool_name: str, tool_input: Dict[str, Any], tool_use_id: str):
        """Add tool use to conversation"""
        # This is typically part of assistant's response
        pass
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages"""
        return self.messages
    
    def clear(self):
        """Clear conversation history"""
        self.messages = []
        self.context = {}
    
    def set_context(self, key: str, value: Any):
        """Store context information"""
        self.context[key] = value
    
    def get_context(self, key: str, default=None) -> Any:
        """Retrieve context information"""
        return self.context.get(key, default)
    
    def _trim_history(self):
        """Trim history to max length"""
        if len(self.messages) > self.max_history:
            # Keep system messages and trim oldest user/assistant pairs
            self.messages = self.messages[-self.max_history:]
    
    def get_summary(self) -> str:
        """Get a summary of conversation"""
        return f"Messages: {len(self.messages)}, Context keys: {list(self.context.keys())}"
