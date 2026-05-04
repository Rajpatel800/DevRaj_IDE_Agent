"""
Test file generation to verify CLI and API use same logic
"""
from orchestrator.simple_engine import SimpleOrchestrator

def test_structured_format():
    """Test with proper ### FILENAME: format"""
    print("\n" + "="*60)
    print("TEST 1: Structured Format")
    print("="*60)
    
    response = """### FILENAME: test1.py
print("Hello from test1")

### FILENAME: test2.py
def greet():
    return "Hello"
"""
    
    orchestrator = SimpleOrchestrator()
    saved = orchestrator.parse_and_save_files(response)
    
    print(f"✅ Saved {len(saved)} files")
    for f in saved:
        print(f"  → {f}")
    
    assert len(saved) == 2, f"Expected 2 files, got {len(saved)}"
    print("✅ TEST PASSED")


def test_markdown_format():
    """Test with markdown code blocks"""
    print("\n" + "="*60)
    print("TEST 2: Markdown Format (should auto-correct)")
    print("="*60)
    
    response = """Here's a simple program:

```python
print("Hello from markdown")
```

This program prints hello."""
    
    orchestrator = SimpleOrchestrator()
    saved = orchestrator.parse_and_save_files(response)
    
    print(f"✅ Saved {len(saved)} files")
    for f in saved:
        print(f"  → {f}")
    
    assert len(saved) == 1, f"Expected 1 file, got {len(saved)}"
    print("✅ TEST PASSED")


def test_mixed_format():
    """Test with explanation + code"""
    print("\n" + "="*60)
    print("TEST 3: Mixed Format (should extract only code)")
    print("="*60)
    
    response = """I'll create a calculator program.

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

print(add(5, 3))

This program adds two numbers."""
    
    orchestrator = SimpleOrchestrator()
    saved = orchestrator.parse_and_save_files(response)
    
    print(f"✅ Saved {len(saved)} files")
    for f in saved:
        print(f"  → {f}")
    
    assert len(saved) == 1, f"Expected 1 file, got {len(saved)}"
    
    # Verify file content is clean (no explanation text)
    with open(saved[0], 'r') as f:
        content = f.read()
    
    assert "I'll create" not in content, "Explanation text found in file!"
    assert "This program" not in content, "Explanation text found in file!"
    assert "def add" in content, "Code not found in file!"
    
    print("✅ TEST PASSED")


def test_cli_method():
    """Test CLI's extract_code_blocks method"""
    print("\n" + "="*60)
    print("TEST 4: CLI Method (extract_code_blocks)")
    print("="*60)
    
    response = """### FILENAME: cli_test.py
print("CLI method test")
"""
    
    orchestrator = SimpleOrchestrator()
    files = orchestrator.extract_code_blocks(response)
    
    print(f"✅ Extracted {len(files)} files")
    for filename, code in files.items():
        print(f"  → {filename}: {len(code)} chars")
    
    assert len(files) == 1, f"Expected 1 file, got {len(files)}"
    assert "cli_test.py" in files, "Filename not found"
    
    print("✅ TEST PASSED")


if __name__ == "__main__":
    print("\n🧪 TESTING FILE GENERATION LOGIC")
    print("="*60)
    
    try:
        test_structured_format()
        test_markdown_format()
        test_mixed_format()
        test_cli_method()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
