"""
Simplified orchestration engine for Claude Opus 4.7 (no tool calling)
With Autopilot Mode
"""
import re
import os
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from bedrock import BedrockClient
from agents import get_agent_prompt
from config import DEFAULT_AGENT, AVAILABLE_AGENTS


class SimpleOrchestrator:
    """Simplified orchestrator without tool calling"""
    
    def __init__(self):
        self.bedrock = BedrockClient()
        self.current_agent = DEFAULT_AGENT
        self.output_dir = "generated_code"
        self.project_root = os.getcwd()
        self.autopilot_enabled = False
        self.max_autopilot_iterations = 5
        self.execution_timeout = 5  # seconds
        
        # Create output directory
        Path(self.output_dir).mkdir(exist_ok=True)
    
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
        elif any(word in user_input_lower for word in ["debug", "fix", "error", "bug", "issue"]):
            return "debugger"
        else:
            return "developer"
    
    def read_file(self, filepath: str) -> Optional[str]:
        """
        Read file content safely (only within project folder)
        
        Args:
            filepath: Path to file
            
        Returns:
            File content or None if error
        """
        try:
            # Normalize path
            full_path = os.path.abspath(filepath)
            
            # Security check: ensure file is within project root
            if not full_path.startswith(self.project_root):
                print(f"⚠️  Security: Cannot read files outside project directory")
                return None
            
            # Check if file exists
            if not os.path.exists(full_path):
                return None
            
            # Read file
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content
            
        except Exception as e:
            return None
    
    def write_file(self, filepath: str, content: str) -> bool:
        """
        Write content to file safely
        
        Args:
            filepath: Path to file
            content: Content to write
            
        Returns:
            True if successful
        """
        try:
            # Normalize path
            full_path = os.path.abspath(filepath)
            
            # Security check
            if not full_path.startswith(self.project_root):
                print(f"⚠️  Security: Cannot write files outside project directory")
                return False
            
            # Create parent directories
            Path(full_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"❌ Error writing file: {e}")
            return False
    
    def is_interactive_program(self, code: str) -> bool:
        """
        Detect if code contains interactive elements
        
        Args:
            code: Source code to check
            
        Returns:
            True if interactive program detected
        """
        interactive_patterns = [
            r'input\s*\(',
            r'while\s+True\s*:',
            r'while\s+1\s*:',
            r'raw_input\s*\(',
        ]
        
        for pattern in interactive_patterns:
            if re.search(pattern, code):
                return True
        
        return False
    
    def get_all_project_files(self) -> Dict[str, str]:
        """
        Read all files in generated_code/ directory
        
        Returns:
            Dict of filename -> content
        """
        files = {}
        
        try:
            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                
                # Only read files (not directories)
                if os.path.isfile(filepath):
                    content = self.read_file(filepath)
                    if content:
                        files[filename] = content
        except Exception as e:
            print(f"⚠️  Error reading project files: {e}")
        
        return files

    def build_stream_context(self, prompt: str, files: list = None) -> str:
        """
        Build enriched prompt that includes all provided workspace file contents.

        Args:
            prompt: User's original prompt
            files: List of dicts with keys 'name', 'relativePath', 'content'

        Returns:
            Full prompt string with file context injected
        """
        if not files:
            return prompt

        context = prompt + "\n\n"
        context += "=== WORKSPACE CONTEXT (files currently open in the project) ===\n"

        for file_info in files:
            name = file_info.get('relativePath', file_info.get('name', 'unknown'))
            content = file_info.get('content', '')
            if not content.strip():
                continue
            context += f"\n--- FILE: {name} ---\n"
            context += content
            context += f"\n--- END OF {name} ---\n"

        context += "\n=== END WORKSPACE CONTEXT ===\n"
        context += "\nUse the workspace context above to understand the existing code before making changes."
        return context

    def extract_files_as_json(self, response: str) -> list:
        """
        Extract all files from AI response and return as a JSON-serializable list.

        Args:
            response: Raw AI response text

        Returns:
            List of dicts: [{filename: str, content: str}]
        """
        files_dict = self.extract_code_blocks(response)
        result = []
        for filename, content in files_dict.items():
            # Strip markdown fences if the AI included them
            content = content.strip()
            content = re.sub(r'^```[\w]*\n', '', content)
            content = re.sub(r'\n```$', '', content)
            content = content.strip()
            if content:
                result.append({'filename': filename, 'content': content})
        return result

    def build_debugger_context(self, error: str) -> str:
        """
        Build comprehensive context for debugger
        
        Args:
            error: Error message
            
        Returns:
            Full context string
        """
        context = "You are an expert debugger.\n\n"
        context += "Here is the complete project:\n\n"
        
        # Get all project files
        files = self.get_all_project_files()
        
        for filename, content in files.items():
            context += f"### FILENAME: {filename}\n"
            context += content
            context += f"\n\n"
        
        context += f"Error occurred:\n{error}\n\n"
        context += "Fix ONLY the necessary files. Return updated files in multi-file format."
        
        return context
    
    def run_code(self, filepath: str) -> Tuple[bool, str, str]:
        """
        Execute Python code safely with enhanced error capture
        
        Args:
            filepath: Path to Python file
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            # Security check: only run files in generated_code/
            if not filepath.startswith(self.output_dir):
                return False, "", "Security: Can only run files in generated_code/"
            
            # Check if file exists
            if not os.path.exists(filepath):
                return False, "", f"File not found: {filepath}"
            
            # Run with timeout
            result = subprocess.run(
                ["python", filepath],
                capture_output=True,
                text=True,
                timeout=self.execution_timeout,
                cwd=self.project_root
            )
            
            # Determine success
            returncode = result.returncode
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            # Success conditions
            if returncode == 0 and stdout:
                return True, stdout, stderr
            elif returncode == 0 and not stdout and not stderr:
                return True, "[No output]", ""
            else:
                return False, stdout, stderr
            
        except subprocess.TimeoutExpired:
            return False, "", f"Execution timeout ({self.execution_timeout}s)"
        except Exception as e:
            return False, "", str(e)
    
    def detect_filenames(self, user_input: str) -> List[str]:
        """
        Detect filenames mentioned in user input
        
        Args:
            user_input: User's message
            
        Returns:
            List of detected filenames
        """
        # Common file extensions
        extensions = [
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.html', '.css', '.scss', '.json', '.xml', '.yaml', '.yml',
            '.txt', '.md', '.sql', '.sh', '.bat', '.go', '.rs', '.php'
        ]
        
        filenames = []
        
        # Pattern: word followed by extension
        for ext in extensions:
            pattern = r'\b(\w+' + re.escape(ext) + r')\b'
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            filenames.extend(matches)
        
        # Also check for paths like "generated_code/app.py"
        path_pattern = r'\b([\w/\\-]+\.\w+)\b'
        path_matches = re.findall(path_pattern, user_input)
        filenames.extend(path_matches)
        
        # Remove duplicates
        return list(set(filenames))
    
    def build_prompt_with_files(self, user_input: str, filenames: List[str]) -> str:
        """
        Build prompt with file contents included
        
        Args:
            user_input: User's message
            filenames: List of files to include
            
        Returns:
            Enhanced prompt with file contents
        """
        prompt = user_input + "\n\n"
        
        for filename in filenames:
            # Try multiple possible paths
            possible_paths = [
                filename,
                os.path.join(self.output_dir, filename),
                os.path.join(self.output_dir, os.path.basename(filename))
            ]
            
            content = None
            used_path = None
            
            for path in possible_paths:
                content = self.read_file(path)
                if content:
                    used_path = path
                    break
            
            if content:
                prompt += f"\n--- Current content of {filename} ---\n"
                prompt += content
                prompt += f"\n--- End of {filename} ---\n\n"
        
        return prompt
    
    def extract_code_blocks(self, response: str) -> Dict[str, str]:
        """
        Extract code blocks from response
        
        Format:
        ### FILENAME: path/to/file.ext
        [code]
        
        Args:
            response: AI response
            
        Returns:
            Dict of filename -> code
        """
        files = {}
        
        # Pattern: ### FILENAME: path/to/file.ext
        pattern = r'###\s*FILENAME:\s*(.+?)\n(.*?)(?=###\s*FILENAME:|$)'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for filename, code in matches:
            filename = filename.strip()
            code = code.strip()
            files[filename] = code
        
        # If no explicit filenames, check for code blocks
        if not files:
            # Look for code blocks (```language ... ```)
            code_pattern = r'```(?:\w+)?\n(.*?)```'
            code_matches = re.findall(code_pattern, response, re.DOTALL)
            
            if code_matches:
                # Save as default file
                files["app.py"] = code_matches[0].strip()
            else:
                # Check if response looks like code (has common code patterns)
                if any(pattern in response for pattern in ["def ", "class ", "import ", "function ", "const ", "var "]):
                    files["app.py"] = response.strip()
        
        return files
    
    def save_files(self, files: Dict[str, str], overwrite_existing: bool = False) -> list:
        """
        Save generated files to disk with automatic backup
        
        Args:
            files: Dict of filename -> code
            overwrite_existing: If True, overwrite files in their original location
            
        Returns:
            List of saved file paths
        """
        saved_files = []
        
        for filename, code in files.items():
            # Determine save path
            if overwrite_existing and os.path.exists(filename):
                filepath = filename
            elif overwrite_existing and os.path.exists(os.path.join(self.output_dir, filename)):
                filepath = os.path.join(self.output_dir, filename)
            else:
                filepath = os.path.join(self.output_dir, filename)
            
            # Backup existing file if it exists
            if os.path.exists(filepath):
                backup_path = self.create_backup(filepath)
                if backup_path:
                    print(f"💾 Backed up: {filepath} → {backup_path}")
            
            # Write file
            if self.write_file(filepath, code):
                saved_files.append(filepath)
                print(f"✅ Saved: {filepath}")
        
        return saved_files
    
    def create_backup(self, filepath: str) -> Optional[str]:
        """
        Create a backup of existing file with timestamp
        
        Args:
            filepath: Path to file to backup
            
        Returns:
            Backup file path or None if failed
        """
        try:
            import datetime
            
            # Create backups directory
            backup_dir = os.path.join(self.output_dir, ".backups")
            Path(backup_dir).mkdir(exist_ok=True)
            
            # Generate backup filename with timestamp
            filename = os.path.basename(filepath)
            name, ext = os.path.splitext(filename)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{name}_{timestamp}{ext}"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Copy file to backup
            content = self.read_file(filepath)
            if content:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return backup_path
            
            return None
            
        except Exception as e:
            print(f"⚠️  Backup failed: {e}")
            return None
    
    def detect_project_name(self, user_input: str, response: str) -> str:
        """
        Detect project name from user input or AI response
        
        Args:
            user_input: User's request
            response: AI's response
            
        Returns:
            Suggested base filename (e.g., "todo_app", "calculator", "streamlit_app")
        """
        # Combine input and response for analysis
        text = (user_input + " " + response).lower()
        
        # Project type patterns (ordered by specificity)
        patterns = [
            # Specific apps
            (r'todo\s+(?:list|app)', 'todo_app'),
            (r'calculator', 'calculator'),
            (r'weather\s+app', 'weather_app'),
            (r'chat\s+(?:bot|app)', 'chatbot'),
            (r'blog', 'blog'),
            (r'portfolio', 'portfolio'),
            (r'dashboard', 'dashboard'),
            (r'game', 'game'),
            (r'snake\s+game', 'snake_game'),
            (r'tic\s*tac\s*toe', 'tictactoe'),
            
            # Framework-specific
            (r'streamlit', 'streamlit_app'),
            (r'flask\s+app', 'flask_app'),
            (r'django', 'django_app'),
            (r'fastapi', 'fastapi_app'),
            (r'react', 'react_app'),
            
            # Generic types
            (r'web\s+app', 'web_app'),
            (r'api', 'api'),
            (r'scraper', 'scraper'),
            (r'bot', 'bot'),
        ]
        
        # Check patterns
        for pattern, name in patterns:
            if re.search(pattern, text):
                return name
        
        # Default fallback
        return "app"
    
    def generate_unique_filename(self, base_name: str = "app", extension: str = ".py") -> str:
        """
        Generate a unique filename with incrementing number
        
        Args:
            base_name: Base name for the file (default: "app")
            extension: File extension (default: ".py")
            
        Returns:
            Unique filename like "todo_app.py", "todo_app_1.py", etc.
        """
        # Try base name first (without number)
        filename = f"{base_name}{extension}"
        filepath = os.path.join(self.output_dir, filename)
        
        if not os.path.exists(filepath):
            return filename
        
        # If exists, add incrementing number
        counter = 1
        while True:
            filename = f"{base_name}_{counter}{extension}"
            filepath = os.path.join(self.output_dir, filename)
            
            if not os.path.exists(filepath):
                return filename
            
            counter += 1
    
    def parse_and_save_files(self, response: str, user_input: str = "", auto_unique: bool = True) -> list:
        """
        Parse response and save files to generated_code/
        ROBUST: Auto-corrects invalid formats, extracts ONLY code
        AUTO-UNIQUE: Automatically generates unique filenames for new projects
        SMART NAMING: Detects project type and uses meaningful names
        
        Args:
            response: AI response text
            user_input: User's original request (for smart naming)
            auto_unique: If True, automatically generate unique filenames (default: True)
            
        Returns:
            List of saved file paths
        """
        # Log raw response for debugging
        print("\n[DEBUG] RAW AI RESPONSE (first 200 chars):")
        print(response[:200] + "..." if len(response) > 200 else response)
        print()
        
        # Clean response - strip markdown
        cleaned = response.strip()
        cleaned = cleaned.replace("```python", "")
        cleaned = cleaned.replace("```", "")
        
        # STRICT PARSING - Try to extract structured format
        files = {}
        # Pattern handles both "### FILENAME: file.py\ncode" and "### FILENAME: file.py code" (no newline)
        pattern = r'###\s*FILENAME:\s*(.+?)(?:\n|\s+)(.*?)(?=###\s*FILENAME:|$)'
        matches = re.findall(pattern, cleaned, re.DOTALL)
        
        if matches:
            # SUCCESS: Found structured format
            for filename, code in matches:
                filename = filename.strip()
                code = code.strip()
                
                if filename and code:
                    # AUTO-UNIQUE: Generate unique filename if file exists and auto_unique is True
                    if auto_unique and os.path.exists(os.path.join(self.output_dir, filename)):
                        # Extract base name and extension
                        base_name, ext = os.path.splitext(filename)
                        if not ext:
                            ext = ".py"
                        unique_filename = self.generate_unique_filename(base_name, ext)
                        print(f"[AUTO-UNIQUE] 🔄 {filename} exists → creating {unique_filename}")
                        filename = unique_filename
                    
                    files[filename] = code
                    print(f"[PARSE] ✅ Extracted: {filename} ({len(code)} chars)")
        else:
            # FALLBACK: AI didn't follow format - extract code intelligently
            print("[WARN] ⚠️  AI response missing ### FILENAME: format")
            print("[AUTO-CORRECT] Extracting code from response...")
            
            # Split response into lines
            lines = response.split('\n')
            code_lines = []
            in_code_block = False
            
            for line in lines:
                # Detect code block markers
                if '```python' in line or '```' in line:
                    in_code_block = not in_code_block
                    continue
                
                # If in code block, collect everything
                if in_code_block:
                    code_lines.append(line)
                    continue
                
                # Detect code patterns (not in markdown block)
                is_code = any([
                    line.strip().startswith('def '),
                    line.strip().startswith('class '),
                    line.strip().startswith('import '),
                    line.strip().startswith('from '),
                    line.strip().startswith('if '),
                    line.strip().startswith('for '),
                    line.strip().startswith('while '),
                    line.strip().startswith('try:'),
                    line.strip().startswith('except'),
                    line.strip().startswith('return '),
                    line.strip().startswith('print('),
                    line.strip().startswith('#'),  # comments
                    (line.strip() and not line[0].isupper() and '=' in line),  # assignments
                    line.strip() == '',  # empty lines in code
                ])
                
                # Skip explanation lines (start with capital, end with period/colon)
                is_explanation = (
                    line.strip() and 
                    line[0].isupper() and 
                    (line.strip().endswith('.') or line.strip().endswith(':')) and
                    'def ' not in line and
                    'class ' not in line
                )
                
                if is_code and not is_explanation:
                    code_lines.append(line)
                elif code_lines and not line.strip():
                    # Keep empty lines within code
                    code_lines.append(line)
            
            # Clean up extracted code
            if code_lines:
                # Remove leading/trailing empty lines
                while code_lines and not code_lines[0].strip():
                    code_lines.pop(0)
                while code_lines and not code_lines[-1].strip():
                    code_lines.pop()
                
                code = '\n'.join(code_lines).strip()
                
                if code:
                    # SMART NAMING: Detect project type from user input
                    if auto_unique and user_input:
                        base_name = self.detect_project_name(user_input, response)
                        filename = self.generate_unique_filename(base_name)
                        print(f"[SMART-NAME] 🎯 Detected project type: {base_name}")
                        print(f"[AUTO-UNIQUE] 🆕 Creating: {filename}")
                    elif auto_unique:
                        filename = self.generate_unique_filename("app")
                        print(f"[AUTO-UNIQUE] 🆕 Creating new file: {filename}")
                    else:
                        filename = "app.py"
                    
                    files[filename] = code
                    print(f"[AUTO-CORRECT] ✅ Extracted {len(code_lines)} lines of code → {filename}")
                else:
                    print("[ERROR] ❌ No code extracted")
                    return []
            else:
                print("[ERROR] ❌ No code detected in response")
                return []
        
        # Validate
        if not files:
            print("[ERROR] ❌ No valid files found")
            return []
        
        # Save files (no backup needed since we're creating unique files)
        saved = self.save_files_no_backup(files)
        print(f"[SUCCESS] ✅ Saved {len(saved)} file(s) to {self.output_dir}")
        for filepath in saved:
            print(f"  → {filepath}")
        
        return saved
    
    def save_files_no_backup(self, files: Dict[str, str]) -> list:
        """
        Save files without backup (for unique filenames)
        
        Args:
            files: Dict of filename -> code
            
        Returns:
            List of saved file paths
        """
        saved_files = []
        
        for filename, code in files.items():
            filepath = os.path.join(self.output_dir, filename)
            
            # Fix formatting if code is on one line (common AI mistake)
            if '\n' not in code and len(code) > 100:
                print(f"[FIX] ⚠️  Detected single-line code, attempting to fix formatting...")
                code = self.fix_code_formatting(code)
            
            # Write file
            if self.write_file(filepath, code):
                saved_files.append(filepath)
                print(f"✅ Saved: {filepath}")
        
        return saved_files
    
    def fix_code_formatting(self, code: str) -> str:
        """
        Fix code that's improperly formatted on one line
        Uses Python's ast module for proper parsing
        
        Args:
            code: Malformed code string
            
        Returns:
            Properly formatted code
        """
        try:
            import ast
            import autopep8
            
            # Try to parse and reformat with autopep8
            formatted = autopep8.fix_code(code)
            return formatted
        except:
            pass
        
        # Fallback: Manual formatting
        # Add spaces after common separators
        code = code.replace(': ', ':\n')
        code = code.replace(' if ', '\nif ')
        code = code.replace(' elif ', '\nelif ')
        code = code.replace(' else:', '\nelse:')
        code = code.replace(' for ', '\nfor ')
        code = code.replace(' while ', '\nwhile ')
        code = code.replace(' def ', '\ndef ')
        code = code.replace(' class ', '\nclass ')
        code = code.replace(' return ', '\nreturn ')
        code = code.replace(' import ', '\nimport ')
        code = code.replace(' from ', '\nfrom ')
        
        # Basic indentation
        lines = code.split('\n')
        formatted_lines = []
        indent = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Dedent for else, elif, except, finally
            if line.startswith(('else:', 'elif ', 'except', 'finally:')):
                indent = max(0, indent - 1)
            
            formatted_lines.append('    ' * indent + line)
            
            # Indent after colon
            if line.rstrip().endswith(':'):
                indent += 1
            
            # Dedent after certain keywords
            if any(line.startswith(kw) for kw in ['return ', 'break', 'continue', 'pass']):
                if indent > 0:
                    indent -= 1
        
        return '\n'.join(formatted_lines)
    
    def autopilot(self, task: str) -> str:
        """
        Autopilot mode: PLAN → BUILD → RUN → DEBUG loop (Production-ready)
        
        Args:
            task: User's task description
            
        Returns:
            Final result message
        """
        print("\n" + "="*60)
        print("🚀 AUTOPILOT MODE ACTIVATED")
        print("="*60)
        
        iteration = 0
        main_file = os.path.join(self.output_dir, "app.py")
        last_error = ""
        previous_code_hash = None
        error_history = []
        
        # Step 1: PLAN
        print("\n[PLAN] Planning the implementation...")
        plan_prompt = get_agent_prompt("planner")
        plan = self.bedrock.call_with_system_prompt(task, plan_prompt)
        print(plan[:500] + "..." if len(plan) > 500 else plan)
        
        while iteration < self.max_autopilot_iterations:
            iteration += 1
            print(f"\n{'='*60}")
            print(f"Iteration {iteration}/{self.max_autopilot_iterations}")
            print(f"{'='*60}")
            
            # Step 2: BUILD
            print("\n[BUILD] Generating code...")
            
            if iteration == 1:
                # First iteration: generate from scratch
                dev_prompt = get_agent_prompt("developer")
                build_task = f"Based on this plan:\n{plan}\n\nImplement: {task}"
                code_response = self.bedrock.call_with_system_prompt(build_task, dev_prompt)
            else:
                # Subsequent iterations: fix based on error with full context
                debug_context = self.build_debugger_context(last_error)
                debug_prompt = get_agent_prompt("debugger")
                code_response = self.bedrock.call_with_system_prompt(debug_context, debug_prompt)
            
            # Extract and save code
            files = self.extract_code_blocks(code_response)
            
            if not files:
                print("❌ No code generated - response not in multi-file format")
                print("⚠️  Retrying with format enforcement...")
                continue
            
            saved_files = self.save_files(files, overwrite_existing=True)
            
            if not saved_files:
                print("❌ Failed to save files")
                break
            
            # Use first saved file as main file (or find main.py/app.py)
            for f in saved_files:
                if 'main.py' in f or 'app.py' in f:
                    main_file = f
                    break
            else:
                main_file = saved_files[0]
            
            print(f"✅ Code saved: {len(saved_files)} file(s)")
            for f in saved_files:
                print(f"   - {f}")
            
            # Check for code changes (prevent infinite loops)
            current_code = self.read_file(main_file)
            if current_code:
                import hashlib
                current_hash = hashlib.md5(current_code.encode()).hexdigest()
                
                if current_hash == previous_code_hash:
                    print("\n[STOPPED] Code unchanged from previous iteration")
                    print("="*60)
                    return "⚠️  Stopped: Code is not changing between iterations"
                
                previous_code_hash = current_hash
            
            # Step 3: INTERACTIVE DETECTION
            if current_code and self.is_interactive_program(current_code):
                print("\n[RUN SKIPPED] Interactive program detected (uses input() or infinite loop)")
                print("[DONE] ✅ Code generated successfully (execution skipped for interactive program)")
                print("="*60)
                return "✅ Interactive program generated successfully\n\n💡 Run manually: python " + main_file
            
            # Step 4: RUN (ALWAYS EXECUTE for non-interactive Python files)
            if not main_file.endswith('.py'):
                print(f"\n[RUN SKIPPED] {os.path.basename(main_file)} is not a Python file")
                print("\n[DONE] ✅ Code generated successfully (execution skipped for web/frontend files)")
                print("="*60)
                return f"✅ Task completed successfully.\n\nGenerated files:\n" + "\n".join([f"- {os.path.basename(f)}" for f in saved_files])
            
            print("\n[RUN] Executing code...")
            success, stdout, stderr = self.run_code(main_file)
            
            # Display output
            if stdout:
                print(f"\n[OUTPUT]")
                print(stdout)
            
            if success:
                print("\n[DONE] ✅ Code executed successfully!")
                print("="*60)
                result = f"✅ Task completed successfully in {iteration} iteration(s)"
                if stdout:
                    result += f"\n\n📤 Output:\n{stdout}"
                return result
            
            # Step 5: ERROR
            print(f"\n[ERROR] ❌ Execution failed")
            last_error = stderr if stderr else "Unknown error"
            print(f"Error details:\n{last_error}")
            
            # Check for repeated errors (prevent infinite loops)
            error_history.append(last_error)
            if len(error_history) >= 2 and error_history[-1] == error_history[-2]:
                print("\n[STOPPED] Same error repeated twice")
                print("="*60)
                return f"⚠️  Stopped: Same error repeating\n\nError:\n{last_error}"
            
            # Step 6: DEBUG (loop continues)
            print("\n[DEBUG] Analyzing error with full project context...")
        
        # Max iterations reached
        print("\n[STOPPED - MAX ITERATIONS] ⚠️ Max iterations reached")
        print("="*60)
        result = f"⚠️ Max iterations ({self.max_autopilot_iterations}) reached."
        if last_error:
            result += f"\n\nLast error:\n{last_error}"
        return result
    
    def process_message(self, user_input: str) -> str:
        """
        Process a user message and return response
        
        Args:
            user_input: User's message
            
        Returns:
            Agent's response
        """
        # AUTOPILOT MODE: Override everything
        if self.autopilot_enabled and not user_input.startswith("/"):
            # Extract task (remove agent mentions)
            task = re.sub(r'@\w+\s*', '', user_input).strip()
            return self.autopilot(task)
        
        # NORMAL MODE: Standard agent flow
        # Detect agent type
        self.current_agent = self.detect_agent(user_input)
        
        # Remove agent mention from input
        clean_input = re.sub(r'@\w+\s*', '', user_input).strip()
        
        # Detect filenames in input
        filenames = self.detect_filenames(clean_input)
        
        # Build prompt with file contents if files are mentioned
        if filenames and self.current_agent in ["developer", "debugger"]:
            enhanced_prompt = self.build_prompt_with_files(clean_input, filenames)
        else:
            enhanced_prompt = clean_input
        
        # Get agent system prompt
        system_prompt = get_agent_prompt(self.current_agent)
        
        print(f"\n🤖 {self.current_agent.title()}: ", end="", flush=True)
        
        try:
            # Call AI
            response = self.bedrock.call_with_system_prompt(
                user_message=enhanced_prompt,
                system_prompt=system_prompt
            )
            
            # If developer or debugger, try to extract and save code
            if self.current_agent in ["developer", "debugger"]:
                files = self.extract_code_blocks(response)
                
                if files:
                    print("\n\n📁 Extracting code files...")
                    
                    # If modifying existing files, overwrite them
                    overwrite = len(filenames) > 0
                    saved_files = self.save_files(files, overwrite_existing=overwrite)
                    
                    if saved_files:
                        response += f"\n\n✅ Saved {len(saved_files)} file(s)"
                        if overwrite:
                            response += " (overwrote existing files)"
            
            return response
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            return error_msg
    
    def toggle_autopilot(self, enable: bool) -> str:
        """Toggle autopilot mode"""
        self.autopilot_enabled = enable
        status = "ON" if enable else "OFF"
        return f"🚀 Autopilot mode: {status}"
    
    def reset(self):
        """Reset the orchestrator state"""
        self.current_agent = DEFAULT_AGENT
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        return {
            "current_agent": self.current_agent,
            "available_agents": AVAILABLE_AGENTS,
            "output_directory": self.output_dir,
            "autopilot_enabled": self.autopilot_enabled
        }
