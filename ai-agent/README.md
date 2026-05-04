# 🤖 Multi-Agent AI Coding System

A Cursor-like multi-agent AI system powered by AWS Bedrock Claude that acts like a professional software team.

## 🎯 Features

- **Role-Based Agents**: Specialized agents for different tasks
  - `@planner` - Software Architect
  - `@developer` - Full-Stack Developer
  - `@debugger` - Bug Fixer
  - `@tester` - QA Engineer

- **Autonomous Tool Usage**: Agents can:
  - Read and write files
  - Execute terminal commands
  - Install packages
  - Debug errors
  - Analyze code quality

- **Intelligent Routing**: Automatically selects the right agent based on your request

- **Conversation Memory**: Maintains context across interactions

## 📋 Prerequisites

- Python 3.8+
- AWS Account with Bedrock access
- AWS credentials configured

## 🚀 Installation

1. **Clone or create the project directory**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up AWS credentials**:

Create a `.env` file or set environment variables:
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

Or configure AWS CLI:
```bash
aws configure
```

## 🎮 Usage

### Start the System

```bash
python main.py
```

### Interact with Agents

**Explicit agent selection**:
```
@planner build a chat application
@developer create a REST API
@debugger fix this error: ModuleNotFoundError
@tester write tests for the API
```

**Automatic agent selection**:
```
Design a microservices architecture  → Uses @planner
Create a login function              → Uses @developer
Fix the import error                 → Uses @debugger
Test the authentication              → Uses @tester
```

### Commands

- `/reset` - Clear conversation history
- `/status` - Show current status
- `/quit` - Exit the system

## 📁 Project Structure

```
ai-agent/
│
├── main.py                 # Entry point
├── config.py              # Configuration
│
├── orchestrator/
│   └── engine.py          # Main orchestration logic
│
├── agents/
│   ├── planner.py         # Architect agent
│   ├── developer.py       # Developer agent
│   ├── debugger.py        # Debugger agent
│   └── tester.py          # Tester agent
│
├── tools/
│   ├── file_tools.py      # File operations
│   ├── terminal_tools.py  # Command execution
│   └── debug_tools.py     # Debugging utilities
│
├── memory/
│   └── memory.py          # Conversation memory
│
└── bedrock/
    └── client.py          # AWS Bedrock client
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Model settings
BEDROCK_MODEL_ID = "anthropic.claude-sonnet-4-20250514"
MAX_TOKENS = 4096
TEMPERATURE = 0.7

# Agent settings
DEFAULT_AGENT = "developer"
MAX_RETRIES = 3
COMMAND_TIMEOUT = 30
```

## 📖 Example Workflows

### 1. Build a Project from Scratch

```
You: @planner build a REST API for a todo app

Planner: [Provides architecture, tech stack, folder structure]

You: @developer start implementing the backend

Developer: [Creates files, writes code, installs dependencies]

You: @tester write tests for the API

Tester: [Creates test files, writes test cases, runs tests]

You: @debugger fix any errors

Debugger: [Analyzes errors, fixes bugs, verifies fixes]
```

### 2. Debug an Existing Project

```
You: @debugger fix this error:
ModuleNotFoundError: No module named 'flask'

Debugger: [Analyzes error, installs flask, verifies fix]
```

### 3. Add a Feature

```
You: @developer add user authentication to the API

Developer: [Reads existing code, implements auth, updates files]

You: @tester test the authentication

Tester: [Writes auth tests, runs them, reports results]
```

## 🛠️ Available Tools

### File Tools
- `read_file(path)` - Read file contents
- `write_file(path, content)` - Write to file
- `list_files(directory)` - List directory contents
- `delete_file(path)` - Delete a file

### Terminal Tools
- `run_command(cmd)` - Execute shell command
- `install_package(package_name, package_manager)` - Install packages

### Debug Tools
- `parse_error(log)` - Parse error messages
- `suggest_fix(error_type, error_message)` - Get fix suggestions
- `analyze_code_quality(code)` - Analyze code quality

## 🔒 Security Notes

- The system executes shell commands - use with caution
- Review generated code before running in production
- Keep AWS credentials secure
- Consider running in isolated environments

## 🚀 Future Enhancements

- [ ] VS Code extension UI
- [ ] Multi-step planning agent
- [ ] Auto-retry system
- [ ] Code diff visualization
- [ ] Web interface
- [ ] Support for more LLM providers
- [ ] Enhanced code analysis
- [ ] Git integration
- [ ] Database tools
- [ ] API testing tools

## 📝 License

MIT License - feel free to use and modify!

## 🤝 Contributing

Contributions welcome! Feel free to:
- Add new agents
- Improve existing tools
- Add new tools
- Enhance prompts
- Fix bugs

## 💡 Tips

1. **Be specific**: Clear instructions get better results
2. **Use the right agent**: Each agent is optimized for specific tasks
3. **Iterate**: Start with planning, then develop, then test
4. **Review output**: Always review generated code
5. **Use /reset**: Clear memory if context gets too large

## 🐛 Troubleshooting

**AWS Credentials Error**:
- Verify AWS credentials are set correctly
- Check Bedrock is enabled in your region
- Ensure you have access to Claude models

**Tool Execution Fails**:
- Check file paths are correct
- Verify permissions
- Review command syntax

**Agent Not Responding**:
- Check internet connection
- Verify AWS Bedrock service status
- Try /reset to clear memory

## 📧 Support

For issues or questions, please check:
- AWS Bedrock documentation
- Claude API documentation
- Project issues on GitHub

---

**Built with ❤️ using AWS Bedrock and Claude**
