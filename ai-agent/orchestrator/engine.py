"""
Main orchestration engine
"""
import re
import json
from typing import Optional, Dict, Any
from bedrock import BedrockClient
from memory import Memory
from agents import get_agent_prompt
from tools import ALL_TOOLS, execute_tool
from config import DEFAULT_AGENT, AVAILABLE_AGENTS, MAX_RETRIES


class Orchestrator:
    """Main orchestration engine for the multi-agent system"""
    
    def __init__(self):
        self.bedrock = BedrockClient()
        self.memory = Memory()
        self.current_agent = DEFAULT_AGENT
        self.max_iterations = 10  # Prevent infinite loops
    
    def detect_agent(self, user_input: str) -> str:
        """
        Detect which agent to use based on user input
        
        Args:
            user_input: User's message
            
        Returns:
            Agent type (planner, developer, debugger, tester)
        """
        user_input_lower = user_input.lower()
        
        # Check for explicit agent mentions
        for agent in AVAILABLE_AGENTS:
            if f"@{agent}" in user_input_lower:
                return agent
        
        # Keyword-based detection
        if any(word in user_input_lower for word in ["plan", "design", "architecture", "structure"]):
            return "planner"
        elif any(word in user_input_lower for word in ["test", "validate", "qa", "verify"]):
            return "tester"
        elif any(word in user_input_lower for word in ["debug", "fix", "error", "bug", "issue"]):
            return "debugger"
        else:
            return "developer"
    
    def process_message(self, user_input: str) -> str:
        """
        Process a user message and return response
        
        Args:
            user_input: User's message
            
        Returns:
            Agent's response
        """
        # Detect agent type
        self.current_agent = self.detect_agent(user_input)
        
        # Remove agent mention from input
        clean_input = re.sub(r'@\w+\s*', '', user_input).strip()
        
        # Add user message to memory
        self.memory.add_user_message(clean_input)
        
        # Get agent system prompt
        system_prompt = get_agent_prompt(self.current_agent)
        
        # Run agent loop
        response = self._agent_loop(system_prompt)
        
        return response
    
    def _agent_loop(self, system_prompt: str) -> str:
        """
        Main agent execution loop with tool calling
        
        Args:
            system_prompt: System prompt for the agent
            
        Returns:
            Final response text
        """
        iteration = 0
        final_response = ""
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # Get messages for API call
            messages = self.memory.get_messages()
            
            # Call Bedrock with tools
            try:
                response = self.bedrock.invoke_with_tools(
                    messages=messages,
                    tools=ALL_TOOLS,
                    system_prompt=system_prompt
                )
            except Exception as e:
                error_msg = f"Error calling Bedrock: {str(e)}"
                print(error_msg)
                return error_msg
            
            # Check stop reason
            stop_reason = response.get("stop_reason")
            
            # Process response content
            content = response.get("content", [])
            
            # Build assistant message
            assistant_message = {"role": "assistant", "content": content}
            self.memory.messages.append(assistant_message)
            
            # Handle different stop reasons
            if stop_reason == "end_turn":
                # Extract text response
                for block in content:
                    if block.get("type") == "text":
                        final_response += block.get("text", "")
                break
            
            elif stop_reason == "tool_use":
                # Process tool calls
                tool_results = []
                
                for block in content:
                    if block.get("type") == "tool_use":
                        tool_name = block.get("name")
                        tool_input = block.get("input", {})
                        tool_use_id = block.get("id")
                        
                        print(f"\n🔧 Using tool: {tool_name}")
                        print(f"   Input: {json.dumps(tool_input, indent=2)}")
                        
                        # Execute tool
                        result = execute_tool(tool_name, tool_input)
                        
                        print(f"   Result: {json.dumps(result, indent=2)[:200]}...")
                        
                        # Add tool result to memory
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": json.dumps(result)
                        })
                
                # Add tool results as user message
                if tool_results:
                    self.memory.messages.append({
                        "role": "user",
                        "content": tool_results
                    })
                
                # Continue loop to get next response
                continue
            
            elif stop_reason == "max_tokens":
                final_response += "\n\n[Response truncated due to length]"
                break
            
            else:
                # Unknown stop reason
                break
        
        if iteration >= self.max_iterations:
            final_response += "\n\n[Max iterations reached]"
        
        return final_response
    
    def reset(self):
        """Reset the orchestrator state"""
        self.memory.clear()
        self.current_agent = DEFAULT_AGENT
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        return {
            "current_agent": self.current_agent,
            "memory_summary": self.memory.get_summary(),
            "available_agents": AVAILABLE_AGENTS
        }
