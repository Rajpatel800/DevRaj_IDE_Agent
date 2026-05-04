# DevRaj IDE Agent - VS Code Extension

A Cursor-like AI coding assistant powered by Claude Opus 4.7, integrated directly into VS Code.

## Features

- 🤖 **Multi-Agent System**: @planner, @developer, @debugger
- 💬 **Sidebar Chat**: Interactive chat interface
- 🚀 **Autopilot Mode**: Automatic plan → build → run → debug loop
- 📝 **Code Generation**: Insert, replace, and create files
- 🔍 **Context-Aware**: Reads active file and workspace
- ⚡ **Streaming Responses**: Real-time word-by-word responses (Cursor-like UX)
- 🎯 **Real-time**: Instant feedback from Opus 4.7 backend

## Installation

### 1. Install Dependencies

```bash
cd vscode-extension
npm install
```

### 2. Start Backend Server

```bash
cd ../ai-agent
pip install fastapi uvicorn
python api_server.py
```

The backend will start at `http://localhost:8000`

### 3. Install Extension

1. Open VS Code
2. Press `F5` to launch Extension Development Host
3. Or package and install:
   ```bash
   npm install -g vsce
   vsce package
   code --install-extension ai-coding-agent-1.0.0.vsix
   ```

## Usage

### Open Chat Sidebar

1. Click the AI Agent icon in the Activity Bar (left sidebar)
2. Or use Command Palette: `AI Agent: Open Chat`

### Chat with AI

```
You: create a Flask hello world app
AI: [Generates code]
```

### Use Agents

- **@planner**: Design architecture and plan implementation
- **@developer**: Generate production-ready code
- **@debugger**: Fix bugs and errors

### Autopilot Mode

1. Toggle "Autopilot Mode" in the sidebar
2. Describe what you want to build
3. AI will automatically:
   - Plan the implementation
   - Generate code
   - Run it
   - Debug errors
   - Repeat until working

### Commands

- `AI Agent: Open Chat` - Open chat sidebar
- `AI Agent: Insert Code` - Insert code at cursor
- `AI Agent: Replace Selection` - Replace selected code
- `AI Agent: Toggle Autopilot` - Enable/disable autopilot

## Configuration

Open VS Code settings and configure:

```json
{
  "aiAgent.apiUrl": "http://localhost:8000"
}
```

## Architecture

```
VS Code Extension (UI)
    ↓ HTTP Request
Python Backend (FastAPI)
    ↓ Claude Opus 4.7 API
AI Agent System
    ↓ Response
VS Code (Update editor/files)
```

## API Endpoints

- `POST /chat` - Send chat message (non-streaming)
- `POST /chat-stream` - Send chat message (streaming)
- `POST /autopilot` - Run autopilot mode
- `POST /file` - File operations
- `GET /status` - Get agent status
- `POST /toggle-autopilot` - Toggle autopilot

### Streaming Support

The extension uses `/chat-stream` endpoint for real-time streaming responses:
- Responses appear word-by-word as they're generated
- Provides immediate feedback (Cursor-like UX)
- Visual indicator shows streaming message

## Development

### Run in Development Mode

```bash
# Terminal 1: Start backend
cd ai-agent
python api_server.py

# Terminal 2: Run extension
cd vscode-extension
code .
# Press F5 to launch Extension Development Host
```

### Debug

1. Set breakpoints in `extension.js`
2. Press `F5` to start debugging
3. Check Debug Console for logs

## Features Comparison

| Feature | Cursor | DevRaj IDE Agent |
|---------|--------|-----------------|
| Chat Interface | ✅ | ✅ |
| Streaming Responses | ✅ | ✅ |
| Code Generation | ✅ | ✅ |
| Multi-Agent | ❌ | ✅ |
| Autopilot Mode | ❌ | ✅ |
| Context-Aware | ✅ | ✅ |
| Free | ❌ | ✅ |

## Troubleshooting

### Backend Not Running

```bash
cd ai-agent
python api_server.py
```

### Extension Not Loading

1. Check VS Code version (requires 1.80+)
2. Reload window: `Ctrl+R` or `Cmd+R`
3. Check Output panel for errors

### API Connection Failed

1. Verify backend is running: `http://localhost:8000`
2. Check firewall settings
3. Update API URL in settings

## License

MIT

## Credits

Built with:
- VS Code Extension API
- FastAPI
- Claude Opus 4.7 (via Bedrock)
- AWS Bedrock
