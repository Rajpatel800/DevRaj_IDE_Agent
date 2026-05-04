# Example: Debugging Session

This example shows how the @debugger agent fixes common errors.

## Scenario 1: Missing Module

```
👤 You: @debugger fix this error:

Traceback (most recent call last):
  File "app.py", line 1, in <module>
    from flask import Flask
ModuleNotFoundError: No module named 'flask'

🤖 Debugger: I'll analyze and fix this error.

[Uses parse_error tool]
Error Analysis:
- Type: ModuleNotFoundError
- Missing module: flask
- Location: app.py, line 1

[Uses suggest_fix tool]
Suggested fixes:
1. Install the missing module using pip install flask
2. Check if the module name is spelled correctly
3. Verify the module is in your requirements.txt

[Uses install_package tool]
Installing flask...

✅ Successfully installed flask

[Uses run_command tool]
Verifying fix...
```bash
python -c "import flask; print(flask.__version__)"
```

Output: 3.0.0

✅ Fix verified! The module is now installed and importable.

The error was caused by a missing dependency. I've installed Flask and verified it works.
```

## Scenario 2: Syntax Error

```
👤 You: @debugger I'm getting a syntax error in my code

🤖 Debugger: I'll help you find and fix the syntax error.

[Uses read_file tool to examine the code]

Found the issue in app.py, line 15:
```python
def hello()
    return "Hello"
```

Problem: Missing colon after function definition

[Uses write_file tool to fix]

Fixed code:
```python
def hello():
    return "Hello"
```

✅ Syntax error fixed!

[Uses run_command to verify]
```bash
python -m py_compile app.py
```

✅ No syntax errors found. The file compiles successfully.
```

## Scenario 3: Logic Error

```
👤 You: @debugger my function returns wrong results

def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

result = calculate_average([])
print(result)  # ZeroDivisionError

🤖 Debugger: I'll analyze and fix this logic error.

[Uses analyze_code_quality tool]

Issue identified: Division by zero when empty list is passed

[Uses write_file to implement fix]

Fixed code:
```python
def calculate_average(numbers):
    if not numbers:
        return 0  # or raise ValueError("Cannot calculate average of empty list")
    
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)
```

Improvements:
1. Added input validation
2. Handle empty list case
3. Prevents ZeroDivisionError

[Uses run_command to test]
```bash
python test_average.py
```

✅ All test cases pass!
- Empty list: returns 0
- Single number: returns that number
- Multiple numbers: returns correct average
```

## Scenario 4: Import Error

```
👤 You: @debugger fix this import error:

ImportError: cannot import name 'create_app' from 'app'

🤖 Debugger: I'll investigate this import error.

[Uses read_file to check app.py]

Analysis:
- File: app.py exists
- Issue: Function 'create_app' is not defined in app.py

[Uses list_files to check structure]

Found:
- app.py contains 'app' variable, not 'create_app' function

[Reads the importing file]

The issue is in main.py:
```python
from app import create_app  # This doesn't exist
```

But app.py has:
```python
app = Flask(__name__)
```

Solution: Update the import statement

[Uses write_file to fix main.py]

Fixed import:
```python
from app import app
```

✅ Import error fixed!

[Verifies the fix]
```bash
python main.py
```

✅ Application starts successfully!
```

## Scenario 5: File Not Found

```
👤 You: @debugger getting FileNotFoundError when reading config

🤖 Debugger: I'll locate and fix this file path issue.

[Uses parse_error tool]

Error: FileNotFoundError: [Errno 2] No such file or directory: 'config.json'

[Uses list_files to check current directory]

Files in current directory:
- app.py
- models.py
- config.yaml (not config.json!)

Issue: The file is named config.yaml but code is looking for config.json

[Uses read_file to check the code]

Found in app.py:
```python
with open('config.json', 'r') as f:
    config = json.load(f)
```

Solution: Either rename the file or update the code

[Uses write_file to fix]

Updated code:
```python
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
```

Also need to install PyYAML:

[Uses install_package]
```bash
pip install pyyaml
```

✅ Fixed! The application now correctly reads config.yaml
```

## Key Debugging Patterns

The debugger agent follows these steps:

1. **Parse Error**: Understand the error message
2. **Locate Source**: Find the file and line causing the issue
3. **Analyze Context**: Read surrounding code
4. **Identify Root Cause**: Determine why it's failing
5. **Implement Fix**: Make targeted changes
6. **Verify Fix**: Run code to confirm it works
7. **Explain**: Document what was wrong and why the fix works

## Common Fixes

- **Missing modules**: Install with pip
- **Syntax errors**: Fix typos, add missing colons/parentheses
- **Import errors**: Check file structure and names
- **Logic errors**: Add validation and error handling
- **File errors**: Verify paths and file existence
- **Type errors**: Add type checking and conversion
