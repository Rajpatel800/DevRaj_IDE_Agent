"""
Test script to verify the system components
"""
import sys
import os

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from bedrock import BedrockClient
        print("✅ Bedrock client imported")
    except Exception as e:
        print(f"❌ Bedrock client import failed: {e}")
        return False
    
    try:
        from memory import Memory
        print("✅ Memory imported")
    except Exception as e:
        print(f"❌ Memory import failed: {e}")
        return False
    
    try:
        from agents import get_agent_prompt
        print("✅ Agents imported")
    except Exception as e:
        print(f"❌ Agents import failed: {e}")
        return False
    
    try:
        from tools import ALL_TOOLS, execute_tool
        print("✅ Tools imported")
    except Exception as e:
        print(f"❌ Tools import failed: {e}")
        return False
    
    try:
        from orchestrator import Orchestrator
        print("✅ Orchestrator imported")
    except Exception as e:
        print(f"❌ Orchestrator import failed: {e}")
        return False
    
    return True


def test_tools():
    """Test tool execution"""
    print("\nTesting tools...")
    
    from tools import execute_tool
    
    # Test list_files
    result = execute_tool("list_files", {"directory": "."})
    if result.get("success"):
        print(f"✅ list_files works ({result['count']} items)")
    else:
        print(f"❌ list_files failed: {result.get('error')}")
        return False
    
    # Test write_file
    result = execute_tool("write_file", {
        "path": "test_output.txt",
        "content": "Test content"
    })
    if result.get("success"):
        print("✅ write_file works")
    else:
        print(f"❌ write_file failed: {result.get('error')}")
        return False
    
    # Test read_file
    result = execute_tool("read_file", {"path": "test_output.txt"})
    if result.get("success") and result.get("content") == "Test content":
        print("✅ read_file works")
    else:
        print(f"❌ read_file failed: {result.get('error')}")
        return False
    
    # Test delete_file
    result = execute_tool("delete_file", {"path": "test_output.txt"})
    if result.get("success"):
        print("✅ delete_file works")
    else:
        print(f"❌ delete_file failed: {result.get('error')}")
        return False
    
    # Test parse_error
    result = execute_tool("parse_error", {
        "log": "ModuleNotFoundError: No module named 'flask'"
    })
    if result.get("success"):
        print("✅ parse_error works")
    else:
        print(f"❌ parse_error failed: {result.get('error')}")
        return False
    
    return True


def test_memory():
    """Test memory system"""
    print("\nTesting memory...")
    
    from memory import Memory
    
    memory = Memory()
    
    # Test adding messages
    memory.add_user_message("Hello")
    memory.add_assistant_message("Hi there!")
    
    messages = memory.get_messages()
    if len(messages) == 2:
        print("✅ Memory stores messages")
    else:
        print("❌ Memory message storage failed")
        return False
    
    # Test context
    memory.set_context("test_key", "test_value")
    value = memory.get_context("test_key")
    if value == "test_value":
        print("✅ Memory context works")
    else:
        print("❌ Memory context failed")
        return False
    
    # Test clear
    memory.clear()
    if len(memory.get_messages()) == 0:
        print("✅ Memory clear works")
    else:
        print("❌ Memory clear failed")
        return False
    
    return True


def test_agents():
    """Test agent prompts"""
    print("\nTesting agents...")
    
    from agents import get_agent_prompt
    
    agents = ["planner", "developer", "debugger", "tester"]
    
    for agent in agents:
        prompt = get_agent_prompt(agent)
        if prompt and len(prompt) > 100:
            print(f"✅ {agent} prompt loaded")
        else:
            print(f"❌ {agent} prompt failed")
            return False
    
    return True


def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    import config
    
    required_vars = [
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "BEDROCK_MODEL_ID",
        "MAX_TOKENS",
        "DEFAULT_AGENT",
        "AVAILABLE_AGENTS"
    ]
    
    for var in required_vars:
        if hasattr(config, var):
            print(f"✅ {var} configured")
        else:
            print(f"❌ {var} missing")
            return False
    
    return True


def test_api_credentials():
    """Test API credentials"""
    print("\nTesting API credentials...")
    
    import config
    
    if config.OPENAI_API_KEY:
        print("✅ OPENAI_API_KEY is set")
    else:
        print("⚠️  OPENAI_API_KEY not set (required for Bedrock)")
        print("   Run: setup_mantle.bat")
    
    if config.OPENAI_BASE_URL:
        print(f"✅ OPENAI_BASE_URL: {config.OPENAI_BASE_URL}")
    else:
        print("⚠️  OPENAI_BASE_URL not set")
    
    print(f"ℹ️  Model: {config.BEDROCK_MODEL_ID}")
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Multi-Agent AI System - Component Tests")
    print("Using Bedrock Mantle API (OpenAI-compatible)")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Tools", test_tools),
        ("Memory", test_memory),
        ("Agents", test_agents),
        ("Configuration", test_config),
        ("API Credentials", test_api_credentials)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Ensure API credentials are set (run setup_mantle.bat)")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run: python main.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
