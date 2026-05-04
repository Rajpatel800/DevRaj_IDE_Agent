const vscode = require('vscode');

const SENTINEL_START = '<<<FILES_JSON>>>';
const SENTINEL_END = '<<<END_FILES>>>';
const MAX_FILE_SIZE = 50 * 1024; // 50 KB
const MAX_CONTEXT_FILES = 10;

let autopilotEnabled = false;

function activate(context) {
    console.log('DevRaj IDE Agent extension activated');

    const config = vscode.workspace.getConfiguration('aiAgent');
    const apiUrl = config.get('apiUrl', 'http://localhost:8000');

    const provider = new ChatViewProvider(context.extensionUri, apiUrl);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('ai-agent-chat', provider)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('ai-agent.openChat', () => {
            vscode.commands.executeCommand('workbench.view.extension.ai-agent-sidebar');
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('ai-agent.insertCode', async () => {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                const code = await vscode.window.showInputBox({ prompt: 'Enter code to insert' });
                if (code) editor.edit(eb => eb.insert(editor.selection.active, code));
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('ai-agent.replaceSelection', async () => {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                const code = await vscode.window.showInputBox({ prompt: 'Enter replacement code' });
                if (code) editor.edit(eb => eb.replace(editor.selection, code));
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('ai-agent.toggleAutopilot', async () => {
            autopilotEnabled = !autopilotEnabled;
            try {
                const res = await fetch(`${apiUrl}/toggle-autopilot?enable=${autopilotEnabled}`, { method: 'POST' });
                if (res.ok) vscode.window.showInformationMessage(`Autopilot ${autopilotEnabled ? 'enabled' : 'disabled'}`);
            } catch (e) {
                vscode.window.showErrorMessage('Failed to toggle autopilot: ' + e.message);
            }
        })
    );

    // Update context badge when editor tabs change
    vscode.window.onDidChangeActiveTextEditor(() => provider.pushContextInfo());
    vscode.workspace.onDidOpenTextDocument(() => provider.pushContextInfo());
    vscode.workspace.onDidCloseTextDocument(() => provider.pushContextInfo());
}

class ChatViewProvider {
    constructor(extensionUri, apiUrl) {
        this._extensionUri = extensionUri;
        this._apiUrl = apiUrl;
        this._view = null;
    }

    resolveWebviewView(webviewView, _context, _token) {
        this._view = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };
        webviewView.webview.html = this._getHtmlForWebview();

        webviewView.webview.onDidReceiveMessage(async data => {
            switch (data.type) {
                case 'sendMessage':
                    await this.handleChatMessage(data.message, data.agent, data.autopilot);
                    break;
                case 'insertCode':
                    await this.insertCode(data.code);
                    break;
                case 'createFile':
                    await this.createFile(data.filename, data.content);
                    break;
                case 'openFile':
                    await this.openFileInEditor(data.path);
                    break;
                case 'getContextInfo':
                    await this.pushContextInfo();
                    break;
            }
        });

        // Push initial context after a short delay
        setTimeout(() => this.pushContextInfo(), 500);
    }

    // ── Context collection ────────────────────────────────────────────────────

    async collectWorkspaceContext() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        const files = [];
        for (const doc of vscode.workspace.textDocuments) {
            if (doc.isUntitled || doc.uri.scheme !== 'file') continue;
            if (doc.getText().length > MAX_FILE_SIZE) continue;
            const relativePath = workspaceFolder
                ? vscode.workspace.asRelativePath(doc.uri, false)
                : doc.fileName.split(/[\\/]/).pop();
            files.push({ name: doc.fileName.split(/[\\/]/).pop(), relativePath, content: doc.getText() });
            if (files.length >= MAX_CONTEXT_FILES) break;
        }
        return files;
    }

    async pushContextInfo() {
        if (!this._view) return;
        const files = await this.collectWorkspaceContext();
        this._view.webview.postMessage({
            type: 'contextInfo',
            fileCount: files.length,
            fileNames: files.map(f => f.relativePath)
        });
    }

    // ── Main message handler ──────────────────────────────────────────────────

    async handleChatMessage(message, agent, autopilot) {
        try {
            this._view.webview.postMessage({ type: 'loading', value: true, agent, autopilot });
            const files = await this.collectWorkspaceContext();
            this._view.webview.postMessage({
                type: 'contextInfo',
                fileCount: files.length,
                fileNames: files.map(f => f.relativePath)
            });

            if (autopilot) {
                const res = await fetch(`${this._apiUrl}/autopilot`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ task: message })
                });
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const result = await res.json();
                this._view.webview.postMessage({ type: 'autopilotComplete', result: result.result });
                return;
            }

            const res = await fetch(`${this._apiUrl}/chat-stream`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: message, agent, system_prompt: agent ? null : '', files })
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const reader = res.body.getReader();
            const decoder = new TextDecoder();

            this._view.webview.postMessage({ type: 'streamStart' });

            // Sentinel-aware streaming
            let buf = '';              // pre-sentinel display buffer
            let jsonBuf = '';          // post-sentinel JSON accumulator
            let sentinelFound = false;

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });

                if (sentinelFound) {
                    jsonBuf += chunk;
                    const endIdx = jsonBuf.indexOf(SENTINEL_END);
                    if (endIdx !== -1) {
                        const jsonStr = jsonBuf.substring(0, endIdx).trim();
                        await this._applyFilesFromJson(jsonStr);
                    }
                } else {
                    buf += chunk;
                    const sIdx = buf.indexOf(SENTINEL_START);
                    if (sIdx !== -1) {
                        // Display everything before the sentinel
                        const before = buf.substring(0, sIdx);
                        if (before) this._view.webview.postMessage({ type: 'streamChunk', chunk: before });
                        sentinelFound = true;
                        jsonBuf = buf.substring(sIdx + SENTINEL_START.length);
                        buf = '';
                        // End sentinel already in same chunk?
                        const endIdx = jsonBuf.indexOf(SENTINEL_END);
                        if (endIdx !== -1) {
                            const jsonStr = jsonBuf.substring(0, endIdx).trim();
                            await this._applyFilesFromJson(jsonStr);
                        }
                    } else {
                        // Safe emit: keep last sentinel-length chars in buffer (boundary safety)
                        const safe = buf.length - SENTINEL_START.length;
                        if (safe > 0) {
                            this._view.webview.postMessage({ type: 'streamChunk', chunk: buf.substring(0, safe) });
                            buf = buf.substring(safe);
                        }
                    }
                }
            }

            // Flush remaining display buffer
            if (buf && !sentinelFound) {
                this._view.webview.postMessage({ type: 'streamChunk', chunk: buf });
            }

            this._view.webview.postMessage({ type: 'streamEnd' });

        } catch (error) {
            this._view.webview.postMessage({ type: 'error', message: error.message });
        } finally {
            this._view.webview.postMessage({ type: 'loading', value: false });
        }
    }

    // ── File application ──────────────────────────────────────────────────────

    async _applyFilesFromJson(jsonStr) {
        let filesList;
        try { filesList = JSON.parse(jsonStr); } catch (e) {
            console.error('[AI Agent] JSON parse error:', e, '\nRaw:', jsonStr.substring(0, 200));
            return;
        }
        const saved = await this.applyFilesToWorkspace(filesList);
        this._view.webview.postMessage({ type: 'filesCreated', files: saved });
    }

    async applyFilesToWorkspace(files) {
        const wsFolder = vscode.workspace.workspaceFolders?.[0];
        if (!wsFolder) {
            vscode.window.showWarningMessage('No workspace folder open — files not saved.');
            return [];
        }

        const saved = [];
        const created = [];
        const updated = [];

        for (const file of files) {
            try {
                const uri = vscode.Uri.joinPath(wsFolder.uri, file.filename);
                // Ensure parent directory exists
                const parentUri = vscode.Uri.joinPath(uri, '..');
                try { await vscode.workspace.fs.createDirectory(parentUri); } catch (_) {}

                // Detect new vs existing
                let exists = false;
                try { await vscode.workspace.fs.stat(uri); exists = true; } catch (_) {}

                await vscode.workspace.fs.writeFile(uri, Buffer.from(file.content, 'utf8'));
                saved.push({ filename: file.filename, fsPath: uri.fsPath, isNew: !exists });
                (exists ? updated : created).push(file.filename);
            } catch (e) {
                console.error(`[AI Agent] Error writing ${file.filename}:`, e);
            }
        }

        if (created.length) {
            vscode.window.showInformationMessage(
                `✨ AI created: ${created.join(', ')}`,
                'Open First'
            ).then(sel => {
                if (sel === 'Open First' && saved.length) {
                    vscode.window.showTextDocument(vscode.Uri.file(saved[0].fsPath));
                }
            });
        }
        if (updated.length) {
            vscode.window.showInformationMessage(`🔄 AI updated: ${updated.join(', ')}`);
        }

        return saved;
    }

    // ── Utility methods ───────────────────────────────────────────────────────

    async insertCode(code) {
        const editor = vscode.window.activeTextEditor;
        if (editor) editor.edit(eb => eb.insert(editor.selection.active, code));
    }

    async createFile(filename, content) {
        const wsFolder = vscode.workspace.workspaceFolders?.[0];
        if (wsFolder) {
            const uri = vscode.Uri.joinPath(wsFolder.uri, filename);
            await vscode.workspace.fs.writeFile(uri, Buffer.from(content, 'utf8'));
            vscode.window.showInformationMessage(`Created ${filename}`);
        }
    }

    async openFileInEditor(relativePath) {
        const wsFolder = vscode.workspace.workspaceFolders?.[0];
        if (!wsFolder) return;
        try {
            const doc = await vscode.workspace.openTextDocument(
                vscode.Uri.joinPath(wsFolder.uri, relativePath)
            );
            await vscode.window.showTextDocument(doc, { preview: false });
        } catch (e) {
            vscode.window.showErrorMessage(`Cannot open ${relativePath}: ${e.message}`);
        }
    }

    // ── Webview HTML ──────────────────────────────────────────────────────────

    _getHtmlForWebview() {
        return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DevRaj IDE Agent</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:var(--vscode-font-family);color:var(--vscode-foreground);background:var(--vscode-editor-background);height:100vh;display:flex;flex-direction:column;font-size:13px}
.header{padding:10px 12px;background:var(--vscode-sideBar-background);border-bottom:1px solid var(--vscode-panel-border);flex-shrink:0}
.header h2{font-size:13px;font-weight:600;margin-bottom:8px;display:flex;align-items:center;gap:6px}
.agent-selector{display:flex;gap:4px;flex-wrap:wrap;margin-bottom:8px}
.agent-btn{padding:3px 8px;font-size:11px;background:var(--vscode-button-secondaryBackground);color:var(--vscode-button-secondaryForeground);border:none;border-radius:3px;cursor:pointer;transition:all 0.15s}
.agent-btn:hover{opacity:0.85}
.agent-btn.active{background:var(--vscode-button-background);color:var(--vscode-button-foreground)}
.autopilot-row{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.toggle{position:relative;width:36px;height:18px;background:var(--vscode-input-background);border-radius:9px;cursor:pointer;transition:background 0.2s;border:1px solid var(--vscode-input-border)}
.toggle.active{background:var(--vscode-button-background)}
.toggle-knob{position:absolute;top:2px;left:2px;width:12px;height:12px;background:#fff;border-radius:50%;transition:transform 0.2s}
.toggle.active .toggle-knob{transform:translateX(18px)}
.context-bar{background:var(--vscode-input-background);border-radius:3px;padding:4px 8px;font-size:11px;color:var(--vscode-descriptionForeground);cursor:pointer;display:flex;align-items:center;gap:4px;border:1px solid var(--vscode-input-border)}
.context-bar:hover{border-color:var(--vscode-focusBorder)}
.ctx-dot{width:6px;height:6px;border-radius:50%;background:var(--vscode-button-background);flex-shrink:0}
.chat{flex:1;overflow-y:auto;padding:10px 12px;display:flex;flex-direction:column;gap:10px}
.msg{border-radius:5px;padding:9px 11px;line-height:1.5}
.msg.user{background:var(--vscode-input-background);border-left:3px solid var(--vscode-button-background)}
.msg.assistant{background:var(--vscode-editor-inactiveSelectionBackground)}
.msg.error{background:var(--vscode-inputValidation-errorBackground, #5c1a1a);border-left:3px solid var(--vscode-errorForeground, #f44)}
.msg-role{font-weight:600;font-size:11px;margin-bottom:5px;opacity:0.7;text-transform:uppercase;letter-spacing:0.5px}
.msg-body{white-space:pre-wrap;word-break:break-word}
.code-wrap{background:var(--vscode-textCodeBlock-background);border-radius:4px;margin:6px 0;overflow:hidden;border:1px solid var(--vscode-panel-border)}
.code-header{display:flex;justify-content:space-between;align-items:center;padding:3px 8px;background:rgba(0,0,0,0.2);font-size:11px}
.code-header .lang{opacity:0.6}
.copy-btn{padding:2px 6px;background:var(--vscode-button-secondaryBackground);color:var(--vscode-button-secondaryForeground);border:none;border-radius:2px;cursor:pointer;font-size:10px}
.copy-btn:hover{background:var(--vscode-button-background);color:var(--vscode-button-foreground)}
pre.code{padding:8px;overflow-x:auto;font-family:var(--vscode-editor-font-family);font-size:12px;margin:0;white-space:pre}
.file-hdr{font-family:var(--vscode-editor-font-family);font-size:11px;color:var(--vscode-button-background);font-weight:600;margin:4px 0 2px}
.files-card{background:var(--vscode-sideBar-background);border:1px solid var(--vscode-panel-border);border-radius:4px;padding:8px 10px;margin-top:6px}
.files-card-title{font-size:11px;font-weight:600;margin-bottom:6px;opacity:0.8}
.file-link{display:flex;align-items:center;gap:6px;padding:3px 0;cursor:pointer;font-size:12px;color:var(--vscode-textLink-foreground)}
.file-link:hover{text-decoration:underline}
.file-badge{font-size:9px;padding:1px 4px;border-radius:2px;font-weight:600}
.badge-new{background:#1a4a1a;color:#4caf50}
.badge-upd{background:#1a3a4a;color:#2196f3}
.typing{display:flex;gap:4px;align-items:center;padding:4px 0}
.typing .dot{width:7px;height:7px;border-radius:50%;background:var(--vscode-descriptionForeground);animation:blink 1.2s infinite}
.typing .dot:nth-child(3){animation-delay:0.2s}
.typing .dot:nth-child(4){animation-delay:0.4s}
@keyframes blink{0%,80%,100%{opacity:0.3;transform:scale(0.9)}40%{opacity:1;transform:scale(1)}}
.input-area{padding:10px 12px;background:var(--vscode-sideBar-background);border-top:1px solid var(--vscode-panel-border);flex-shrink:0}
textarea.inp{width:100%;padding:7px 9px;background:var(--vscode-input-background);color:var(--vscode-input-foreground);border:1px solid var(--vscode-input-border);border-radius:3px;font-family:var(--vscode-font-family);font-size:13px;resize:vertical;min-height:60px;outline:none;transition:border-color 0.15s}
textarea.inp:focus{border-color:var(--vscode-focusBorder)}
.send-btn{margin-top:5px;width:100%;padding:7px;background:var(--vscode-button-background);color:var(--vscode-button-foreground);border:none;border-radius:3px;cursor:pointer;font-size:13px;font-weight:500;transition:opacity 0.15s}
.send-btn:hover{opacity:0.9}
.send-btn:disabled{opacity:0.4;cursor:not-allowed}
.hint{font-size:11px;color:var(--vscode-descriptionForeground);margin-top:4px;text-align:right}
#stream-msg{border-left:3px solid var(--vscode-button-background)}
</style>
</head>
<body>
<div class="header">
  <h2>🤖 DevRaj IDE Agent</h2>
  <div class="agent-selector">
    <button class="agent-btn active" data-agent="">Auto</button>
    <button class="agent-btn" data-agent="planner">@planner</button>
    <button class="agent-btn" data-agent="developer">@developer</button>
    <button class="agent-btn" data-agent="debugger">@debugger</button>
  </div>
  <div class="autopilot-row">
    <div class="toggle" id="apToggle"><div class="toggle-knob"></div></div>
    <span style="font-size:12px">Autopilot</span>
  </div>
  <div class="context-bar" id="ctxBar" title="Files currently in context">
    <div class="ctx-dot"></div>
    <span id="ctxLabel">0 files in context</span>
  </div>
</div>

<div class="chat" id="chat"></div>

<div class="input-area">
  <textarea class="inp" id="inp" placeholder="Ask AI to generate code, fix bugs, or plan…"></textarea>
  <button class="send-btn" id="sendBtn">Send  (Ctrl+Enter)</button>
  <div class="hint">Ctrl+Enter to send</div>
</div>

<script>
const vscode = acquireVsCodeApi();
let selectedAgent = '';
let autopilot = false;
let loading = false;
let streamEl = null;
let streamRaw = '';
let ctxFiles = [];

// Agent buttons
document.querySelectorAll('.agent-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.agent-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedAgent = btn.dataset.agent;
  });
});

// Autopilot toggle
document.getElementById('apToggle').addEventListener('click', () => {
  autopilot = !autopilot;
  document.getElementById('apToggle').classList.toggle('active', autopilot);
});

// Context bar tooltip
document.getElementById('ctxBar').addEventListener('click', () => {
  if (ctxFiles.length === 0) return;
  const tip = ctxFiles.join('\\n');
  vscode.postMessage({ type: 'showInfo', text: tip });
});

// Send
document.getElementById('sendBtn').addEventListener('click', send);
document.getElementById('inp').addEventListener('keydown', e => {
  if (e.key === 'Enter' && e.ctrlKey) { e.preventDefault(); send(); }
});

function send() {
  if (loading) return;
  const inp = document.getElementById('inp');
  const msg = inp.value.trim();
  if (!msg) return;
  addMsg('user', msg);
  inp.value = '';
  vscode.postMessage({ type: 'sendMessage', message: msg, agent: selectedAgent, autopilot });
}

function escHtml(t) {
  return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function renderContent(text) {
  let parts = text.split(/(\\\`\\\`\\\`[\\w]*\\n[\\s\\S]*?\\\`\\\`\\\`)/g);
  let html = '';
  for (let part of parts) {
    const cbMatch = part.match(/^\\\`\\\`\\\`([\\w]*)\\n([\\s\\S]*)\\\`\\\`\\\`$/);
    if (cbMatch) {
      const lang = cbMatch[1] || 'code';
      const code = escHtml(cbMatch[2]);
      html += \`<div class="code-wrap"><div class="code-header"><span class="lang">\${lang}</span><button class="copy-btn" onclick="doCopy(this)">Copy</button></div><pre class="code"><code>\${code}</code></pre></div>\`;
    } else {
      // Highlight ### FILENAME: lines
      let t2 = escHtml(part);
      t2 = t2.replace(/### FILENAME: (.+)/g, '<div class="file-hdr">📄 $1</div>');
      html += \`<span class="msg-body">\${t2}</span>\`;
    }
  }
  return html;
}

function doCopy(btn) {
  const code = btn.closest('.code-wrap').querySelector('code').innerText;
  navigator.clipboard.writeText(code).then(() => {
    btn.textContent = 'Copied!';
    setTimeout(() => btn.textContent = 'Copy', 1500);
  });
}

function addMsg(role, content) {
  const chat = document.getElementById('chat');
  const div = document.createElement('div');
  div.className = 'msg ' + role;
  const roleLabel = role === 'user' ? 'You' : role === 'error' ? '⚠ Error' : '🤖 Agent';
  div.innerHTML = \`<div class="msg-role">\${roleLabel}</div><div class="msg-body">\${renderContent(content)}</div>\`;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

function showTyping(label = 'Thinking') {
  const chat = document.getElementById('chat');
  const div = document.createElement('div');
  div.className = 'msg assistant';
  div.id = 'typing-ind';
  div.innerHTML = \`<div class="msg-role">🤖 Agent</div><div class="typing"><span style="margin-right:8px;font-size:11px;opacity:0.8;font-weight:500">\${label}</span><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>\`;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}
function removeTyping() { const el = document.getElementById('typing-ind'); if (el) el.remove(); }

// Message handler
window.addEventListener('message', ev => {
  const msg = ev.data;
  switch (msg.type) {
    case 'loading':
      loading = msg.value;
      document.getElementById('sendBtn').disabled = loading;
      if (loading) {
        let label = 'Thinking';
        if (msg.autopilot) label = 'Autopilot running';
        else if (msg.agent === 'planner') label = 'Planning';
        else if (msg.agent === 'developer') label = 'Generating code';
        else if (msg.agent === 'debugger') label = 'Debugging';
        showTyping(label);
      } else {
        removeTyping();
      }
      break;

    case 'contextInfo':
      ctxFiles = msg.fileNames || [];
      document.getElementById('ctxLabel').textContent =
        ctxFiles.length === 0 ? 'No files in context'
        : ctxFiles.length === 1 ? '1 file in context'
        : \`\${ctxFiles.length} files in context\`;
      break;

    case 'streamStart':
      removeTyping();
      streamRaw = '';
      const chat = document.getElementById('chat');
      const div = document.createElement('div');
      div.className = 'msg assistant';
      div.id = 'stream-msg';
      div.innerHTML = '<div class="msg-role">🤖 Agent</div><div id="stream-body" class="msg-body"></div>';
      chat.appendChild(div);
      streamEl = document.getElementById('stream-body');
      break;

    case 'streamChunk':
      if (streamEl) {
        streamRaw += msg.chunk;
        streamEl.innerHTML = renderContent(streamRaw);
        document.getElementById('chat').scrollTop = document.getElementById('chat').scrollHeight;
      }
      break;

    case 'streamEnd':
      const sm = document.getElementById('stream-msg');
      if (sm) sm.removeAttribute('id');
      streamEl = null;
      streamRaw = '';
      break;

    case 'filesCreated':
      if (msg.files && msg.files.length) {
        const chat2 = document.getElementById('chat');
        const card = document.createElement('div');
        card.className = 'msg assistant';
        let inner = '<div class="files-card"><div class="files-card-title">📁 Files written to workspace</div>';
        msg.files.forEach(f => {
          const badge = f.isNew
            ? '<span class="file-badge badge-new">NEW</span>'
            : '<span class="file-badge badge-upd">UPDATED</span>';
          inner += \`<div class="file-link" onclick="openFile('\${f.filename}')">\${badge} \${escHtml(f.filename)}</div>\`;
        });
        inner += '</div>';
        card.innerHTML = inner;
        chat2.appendChild(card);
        chat2.scrollTop = chat2.scrollHeight;
      }
      break;

    case 'error':
      removeTyping();
      addMsg('error', msg.message);
      break;

    case 'autopilotComplete':
      removeTyping();
      addMsg('assistant', msg.result || 'Autopilot finished.');
      break;

    case 'response':
      addMsg('assistant', msg.message);
      break;
  }
});

function openFile(path) {
  vscode.postMessage({ type: 'openFile', path });
}

// Request initial context
vscode.postMessage({ type: 'getContextInfo' });
</script>
</body>
</html>`;
    }
}

function deactivate() {}

module.exports = { activate, deactivate };
