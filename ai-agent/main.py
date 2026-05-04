"""
Main entry point for the AI Agent System (Claude Opus 4.7 Version)
With Autopilot Mode
"""
import sys
from orchestrator.simple_engine import SimpleOrchestrator


def print_banner():
    """Print welcome banner"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║     🤖 Multi-Agent AI Coding System                     ║
║                                                          ║
║                                                          ║
║  Available Agents:                                       ║
║    @planner   - Software Architect                       ║
║    @developer - Full-Stack Developer                     ║
║    @debugger  - Bug Fixer                                ║
║                                                          ║
║  Commands:                                               ║
║    /autopilot on  - Enable autopilot mode                ║
║    /autopilot off - Disable autopilot mode               ║
║    /reset         - Clear conversation history           ║
║    /status        - Show current status                  ║
║    /quit          - Exit the system                      ║
║                                                          ║
║  🚀 Autopilot Mode:                                      ║
║    Automatically: PLAN → BUILD → RUN → DEBUG → REPEAT   ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)


def main():
    """Main interactive loop"""
    print_banner()
    
    orchestrator = SimpleOrchestrator()
    
    print("\n💬 Start chatting with the AI agents!")
    print("   (Type your message or use @ to specify an agent)\n")
    print(f"📁 Generated code will be saved to: {orchestrator.output_dir}/\n")
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith("/"):
                command = user_input[1:].lower()
                
                if command == "quit" or command == "exit":
                    print("\n👋 Goodbye!")
                    break
                
                elif command == "reset":
                    orchestrator.reset()
                    print("\n✅ Conversation reset!")
                    continue
                
                elif command.startswith("autopilot"):
                    parts = command.split()
                    if len(parts) == 2 and parts[1] in ["on", "off"]:
                        enable = parts[1] == "on"
                        result = orchestrator.toggle_autopilot(enable)
                        print(f"\n{result}")
                        if enable:
                            print("\n💡 Tip: Just describe what you want to build, and the system will:")
                            print("   1. Plan the implementation")
                            print("   2. Generate code")
                            print("   3. Run it")
                            print("   4. Debug errors automatically")
                            print("   5. Repeat until it works!")
                    else:
                        print("\n❌ Usage: /autopilot on  or  /autopilot off")
                    continue
                
                elif command == "status":
                    status = orchestrator.get_status()
                    print(f"\n📊 Status:")
                    print(f"   Current Agent: {status['current_agent']}")
                    print(f"   Output Directory: {status['output_directory']}")
                    print(f"   Autopilot: {'ON 🚀' if status['autopilot_enabled'] else 'OFF'}")
                    print(f"   Available Agents: {', '.join(status['available_agents'])}")
                    continue
                
                else:
                    print(f"\n❌ Unknown command: {command}")
                    continue
            
            # Process message
            response = orchestrator.process_message(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("   Please try again or type /reset to start over")


if __name__ == "__main__":
    main()

