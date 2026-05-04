"""
Test automatic unique filename generation
"""
from orchestrator.simple_engine import SimpleOrchestrator

def test_auto_unique():
    """Test that each new program gets a unique filename"""
    print("\n" + "="*60)
    print("TEST: Automatic Unique Filename Generation")
    print("="*60)
    
    orchestrator = SimpleOrchestrator()
    
    # Create first program
    print("\n1. Creating first program...")
    response1 = """### FILENAME: app.py
print("Program 1")"""
    
    saved1 = orchestrator.parse_and_save_files(response1)
    print(f"✅ Created: {saved1}")
    
    # Create second program (should auto-create app_1.py)
    print("\n2. Creating second program...")
    response2 = """### FILENAME: app.py
print("Program 2")"""
    
    saved2 = orchestrator.parse_and_save_files(response2)
    print(f"✅ Created: {saved2}")
    
    # Create third program (should auto-create app_2.py)
    print("\n3. Creating third program...")
    response3 = """### FILENAME: app.py
print("Program 3")"""
    
    saved3 = orchestrator.parse_and_save_files(response3)
    print(f"✅ Created: {saved3}")
    
    # Verify all files exist with correct content
    print("\n4. Verifying files...")
    
    import os
    files_to_check = [
        ("generated_code/app.py", "Program 1"),
        ("generated_code/app_1.py", "Program 2"),
        ("generated_code/app_2.py", "Program 3"),
    ]
    
    all_correct = True
    for filepath, expected_content in files_to_check:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            
            if expected_content in content:
                print(f"✅ {filepath} - Correct content")
            else:
                print(f"❌ {filepath} - Wrong content")
                all_correct = False
        else:
            print(f"❌ {filepath} - File not found")
            all_correct = False
    
    print("\n" + "="*60)
    if all_correct:
        print("✅ ALL TESTS PASSED - Each program has unique file!")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*60)
    
    return all_correct


def test_without_filename():
    """Test auto-unique when AI doesn't specify filename"""
    print("\n" + "="*60)
    print("TEST: Auto-Unique Without Filename")
    print("="*60)
    
    orchestrator = SimpleOrchestrator()
    
    # Create programs without ### FILENAME: format
    print("\n1. Creating program without filename...")
    response1 = """print("Hello World 1")"""
    saved1 = orchestrator.parse_and_save_files(response1)
    print(f"✅ Created: {saved1}")
    
    print("\n2. Creating another program without filename...")
    response2 = """print("Hello World 2")"""
    saved2 = orchestrator.parse_and_save_files(response2)
    print(f"✅ Created: {saved2}")
    
    print("\n3. Creating third program without filename...")
    response3 = """print("Hello World 3")"""
    saved3 = orchestrator.parse_and_save_files(response3)
    print(f"✅ Created: {saved3}")
    
    # Check that different files were created
    if len(set(saved1 + saved2 + saved3)) == 3:
        print("\n✅ All programs saved to unique files!")
        return True
    else:
        print("\n❌ Files were overwritten")
        return False


if __name__ == "__main__":
    print("\n🧪 TESTING AUTO-UNIQUE FILENAME GENERATION")
    
    test1 = test_auto_unique()
    test2 = test_without_filename()
    
    print("\n" + "="*60)
    if test1 and test2:
        print("✅ ALL TESTS PASSED")
        print("🎉 Every new program gets a unique filename!")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*60)
