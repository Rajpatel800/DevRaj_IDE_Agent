"""
Agent role definitions
"""
from .planner import get_planner_prompt
from .developer import get_developer_prompt
from .debugger import get_debugger_prompt
from .tester import get_tester_prompt


AGENT_PROMPTS = {
    "planner": get_planner_prompt,
    "developer": get_developer_prompt,
    "debugger": get_debugger_prompt,
    "tester": get_tester_prompt
}


def get_agent_prompt(agent_type: str) -> str:
    """
    Get system prompt for specified agent type
    
    Args:
        agent_type: Type of agent (planner, developer, debugger, tester)
        
    Returns:
        System prompt string
    """
    if agent_type not in AGENT_PROMPTS:
        agent_type = "developer"  # Default to developer
    
    return AGENT_PROMPTS[agent_type]()


__all__ = [
    'AGENT_PROMPTS',
    'get_agent_prompt'
]
