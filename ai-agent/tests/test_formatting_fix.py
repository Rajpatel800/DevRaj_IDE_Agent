"""
Test code formatting fix
"""
from orchestrator.simple_engine import SimpleOrchestrator

def test_single_line_code():
    """Test fixing code that's all on one line"""
    print("\n" + "="*60)
    print("TEST: Fix Single-Line Code")
    print("="*60)
    
    orchestrator = SimpleOrchestrator()
    
    # Simulate malformed code (all on one line)
    malformed_code = 'nterms = int(input("How many terms? ")) if nterms <= 0: print("Please enter a positive integer") else: n1, n2 = 0, 1 count = 0 fib_series = [] while count < nterms: fib_series.append(n1) nth = n1 + n2 n1 = n2 n2 = nth count += 1 print("Fibonacci sequence:", fib_series)'
    
    print("\nOriginal (malformed):")
    print(malformed_code[:100] + "...")
    
    # Fix it
    fixed_code = orchestrator.fix_code_formatting(malformed_code)
    
    print("\nFixed:")
    print(fixed_code)
    
    # Save to file
    files = {"fibonacci_fixed.py": fixed_code}
    saved = orchestrator.save_files_no_backup(files)
    
    if saved:
        print(f"\n✅ Saved to: {saved[0]}")
        return True
    else:
        print("\n❌ Failed to save")
        return False


if __name__ == "__main__":
    print("\n🧪 TESTING CODE FORMATTING FIX")
    
    result = test_single_line_code()
    
    print("\n" + "="*60)
    if result:
        print("✅ FORMATTING FIX WORKING!")
    else:
        print("❌ TEST FAILED")
    print("="*60)
