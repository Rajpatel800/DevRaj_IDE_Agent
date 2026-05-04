"""
FastAPI server for VS Code Extension backend
With Streaming Support
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import json
import re
import sys

# Force UTF-8 for Windows console
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from orchestrator.simple_engine import SimpleOrchestrator
from agents import get_agent_prompt

app = FastAPI(title="DevRaj IDE Agent API")

# Enable CORS for VS Code extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator = SimpleOrchestrator()


class ChatRequest(BaseModel):
    message: str
    agent: Optional[str] = None
    files: Optional[List[dict]] = None
    autopilot: bool = False


class ChatResponse(BaseModel):
    response: str
    files_created: Optional[List[str]] = None
    success: bool = True


class StreamRequest(BaseModel):
    prompt: str
    agent: Optional[str] = None
    system_prompt: Optional[str] = None
    files: Optional[List[dict]] = None  # workspace context files from VS Code


class AutopilotRequest(BaseModel):
    task: str


class FileOperation(BaseModel):
    operation: str  # "read", "write", "create"
    filepath: str
    content: Optional[str] = None


@app.get("/")
async def root():
    """Health check"""
    return {"status": "running", "message": "DevRaj IDE Agent API"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat message (non-streaming)
    UNIFIED: Uses same pipeline as CLI
    """
    try:
        # Build message with agent mention if specified
        message = request.message
        if request.agent:
            message = f"@{request.agent} {message}"
        
        # Add file context if provided
        if request.files:
            for file_info in request.files:
                message += f"\n\n--- {file_info['name']} ---\n"
                message += file_info['content']
                message += f"\n--- End of {file_info['name']} ---\n"
        
        print(f"\n[API] Processing: {message[:100]}...")
        
        # Use orchestrator's process_message (SAME AS CLI)
        if request.autopilot:
            orchestrator.autopilot_enabled = True
            response = orchestrator.process_message(message)
            orchestrator.autopilot_enabled = False
        else:
            response = orchestrator.process_message(message)
        
        return ChatResponse(
            response=response,
            success=True
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat-stream")
async def chat_stream(request: StreamRequest):
    """
    Process chat message with streaming response
    UNIFIED: Uses same pipeline as CLI
    """
    try:
        prompt = request.prompt
        agent = request.agent
        
        # Build full prompt with agent mention (like CLI)
        if agent:
            full_prompt = f"@{agent} {prompt}"
        else:
            full_prompt = prompt
        
        print(f"\n[API] Processing: {full_prompt[:100]}...")
        print(f"[API] Agent: {agent if agent else 'auto-detect'}")
        print(f"[API] Workspace files received: {len(request.files or [])}")

        # Detect agent
        detected_agent = orchestrator.detect_agent(full_prompt)
        print(f"[API] Detected agent: {detected_agent}")

        # Clean input
        clean_input = re.sub(r'@\w+\s*', '', full_prompt).strip()

        # Inject workspace file context
        enriched_input = orchestrator.build_stream_context(clean_input, request.files)

        # Get system prompt
        system_prompt = get_agent_prompt(detected_agent)
        print(f"[API] Using {detected_agent} system prompt")

        # Collect full response for file extraction
        full_response = ""

        SENTINEL_START = "<<<FILES_JSON>>>"
        SENTINEL_END = "<<<END_FILES>>>"

        # Stream generator
        def generate():
            nonlocal full_response
            try:
                # Stream AI response
                for chunk in orchestrator.bedrock.call_with_system_prompt_stream(
                    enriched_input, system_prompt
                ):
                    full_response += chunk
                    yield chunk

                print(f"\n[API] Full response received ({len(full_response)} chars)")

                # After streaming: extract files and emit sentinel for VS Code extension
                if detected_agent in ["developer", "debugger"]:
                    print("[API] Extracting code files for VS Code...")
                    files_list = orchestrator.extract_files_as_json(full_response)

                    if files_list:
                        print(f"[API] Found {len(files_list)} file(s) — emitting sentinel")
                        import json as _json
                        yield f"\n{SENTINEL_START}\n"
                        yield _json.dumps(files_list, ensure_ascii=False)
                        yield f"\n{SENTINEL_END}\n"
                    else:
                        yield "\n\n⚠️  No code files detected in response"
                else:
                    print(f"[API] Agent '{detected_agent}' — no file extraction")

            except Exception as e:
                print(f"[API ERROR] {str(e)}")
                yield f"\n\n❌ Error: {str(e)}"

        return StreamingResponse(
            generate(),
            media_type="text/plain"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/autopilot")
async def autopilot(request: AutopilotRequest):
    """
    Run autopilot mode
    """
    try:
        result = orchestrator.autopilot(request.task)
        
        return {
            "success": True,
            "result": result,
            "files": orchestrator.get_all_project_files()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/file")
async def file_operation(request: FileOperation):
    """
    Perform file operations
    """
    try:
        if request.operation == "read":
            content = orchestrator.read_file(request.filepath)
            return {"success": True, "content": content}
        
        elif request.operation == "write":
            success = orchestrator.write_file(request.filepath, request.content)
            return {"success": success}
        
        else:
            raise HTTPException(status_code=400, detail="Invalid operation")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """
    Get orchestrator status
    """
    return orchestrator.get_status()


@app.post("/toggle-autopilot")
async def toggle_autopilot(enable: bool):
    """
    Toggle autopilot mode
    """
    result = orchestrator.toggle_autopilot(enable)
    return {"message": result, "enabled": enable}


if __name__ == "__main__":
    import socket
    def find_free_port(start_port=8000, max_port=8100):
        for port in range(start_port, max_port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
        return start_port
        
    port = find_free_port(8000)
    print("🚀 Starting DevRaj IDE Agent API Server...")
    print(f"📡 Server will be available at: http://localhost:{port}")
    print(f"📖 API docs: http://localhost:{port}/docs")
    print("✨ Streaming support enabled")
    
    if port != 8000:
        print("="*60)
        print(f"⚠️  PORT 8000 WAS BUSY! Server automatically started on port {port}.")
        print(f"⚠️  Please update 'aiAgent.apiUrl' in VS Code settings to: http://localhost:{port}")
        print("="*60)
        
    uvicorn.run(app, host="0.0.0.0", port=port)
