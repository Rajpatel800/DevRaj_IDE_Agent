"""
Test parser fix for format without newline
"""
from orchestrator.simple_engine import SimpleOrchestrator

def test_no_newline_format():
    """Test format: ### FILENAME: app.py print("code")"""
    print("\n" + "="*60)
    print("TEST: Format without newline after filename")
    print("="*60)
    
    # This is what the AI returned
    response = """### FILENAME: app.py print("I love AI agent")"""
    
    orchestrator = SimpleOrchestrator()
    saved = orchestrator.parse_and_save_files(response)
    
    print(f"\n✅ Saved {len(saved)} files")
    
    if saved:
        # Read the file
        with open(saved[0], 'r') as f:
            content = f.read()
        
        print(f"\nFile content:")
        print("-" * 60)
        print(content)
        print("-" * 60)
        
        # Verify
        if "### FILENAME:" in content:
            print("\n❌ FAILED: File contains header")
            return False
        elif 'print("I love AI agent")' in content:
            print("\n✅ PASSED: File contains only code")
            return True
        else:
            print("\n⚠️  UNEXPECTED: File content is different")
            return False
    else:
        print("\n❌ FAILED: No files saved")
        return False


def test_proper_format():
    """Test format: ### FILENAME: app.py\nprint("code")"""
    print("\n" + "="*60)
    print("TEST: Proper format with newline")
    print("="*60)
    
    response = """### FILENAME: test_proper.py
print("Proper format")"""
    
    orchestrator = SimpleOrchestrator()
    saved = orchestrator.parse_and_save_files(response)
    
    print(f"\n✅ Saved {len(saved)} files")
    
    if saved:
        with open(saved[0], 'r') as f:
            content = f.read()
        
        print(f"\nFile content:")
        print("-" * 60)
        print(content)
        print("-" * 60)
        
        if 'print("Proper format")' in content and "### FILENAME:" not in content:
            print("\n✅ PASSED")
            return True
        else:
            print("\n❌ FAILED")
            return False
    else:
        print("\n❌ FAILED: No files saved")
        return False


if __name__ == "__main__":
    print("\n🧪 TESTING PARSER FIX")
    
    test1 = test_no_newline_format()
    test2 = test_proper_format()
    
    print("\n" + "="*60)
    if test1 and test2:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*60)
