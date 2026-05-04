"""
Test multi-file project handling
"""
from orchestrator.simple_engine import SimpleOrchestrator

def test_multifile_project():
    """Test that system handles multiple files in one response"""
    print("\n" + "="*60)
    print("TEST: Multi-File Project")
    print("="*60)
    
    orchestrator = SimpleOrchestrator()
    
    # Simulate AI response with multiple files
    response = """### FILENAME: main.py
import utils
import config

def main():
    print("Main application")
    utils.helper()

if __name__ == "__main__":
    main()

### FILENAME: utils.py
def helper():
    print("Helper function")

def process_data(data):
    return data.upper()

### FILENAME: config.py
DATABASE_URL = "sqlite:///app.db"
DEBUG = True
PORT = 8000

### FILENAME: requirements.txt
flask==2.3.0
requests==2.31.0
"""
    
    user_input = "create a flask app with proper structure"
    
    print("\n📝 Creating multi-file project...")
    saved = orchestrator.parse_and_save_files(response, user_input)
    
    print(f"\n✅ Created {len(saved)} files:")
    for filepath in saved:
        filename = filepath.split('\\')[-1].split('/')[-1]
        print(f"   • {filename}")
    
    # Verify all files were created
    expected_files = ["main.py", "utils.py", "config.py", "requirements.txt"]
    created_files = [f.split('\\')[-1].split('/')[-1] for f in saved]
    
    print("\n🔍 Verification:")
    all_created = True
    for expected in expected_files:
        if expected in created_files:
            print(f"   ✅ {expected} - Created")
        else:
            print(f"   ❌ {expected} - Missing")
            all_created = False
    
    if all_created:
        print("\n✅ ALL FILES CREATED SUCCESSFULLY!")
        return True
    else:
        print("\n❌ SOME FILES MISSING")
        return False


def test_multifile_with_folders():
    """Test multi-file project with folder structure"""
    print("\n" + "="*60)
    print("TEST: Multi-File with Folders")
    print("="*60)
    
    orchestrator = SimpleOrchestrator()
    
    # Simulate AI response with folder structure
    response = """### FILENAME: app.py
from src.core import Calculator

calc = Calculator()
print(calc.add(5, 3))

### FILENAME: src/core.py
class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b

### FILENAME: src/__init__.py
# Package initialization

### FILENAME: tests/test_calculator.py
from src.core import Calculator

def test_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5
"""
    
    user_input = "create a calculator project with tests"
    
    print("\n📝 Creating project with folder structure...")
    saved = orchestrator.parse_and_save_files(response, user_input)
    
    print(f"\n✅ Created {len(saved)} files:")
    for filepath in saved:
        # Show relative path from generated_code
        rel_path = filepath.replace('generated_code\\', '').replace('generated_code/', '')
        print(f"   • {rel_path}")
    
    if len(saved) == 4:
        print("\n✅ ALL FILES WITH FOLDERS CREATED!")
        return True
    else:
        print(f"\n⚠️  Expected 4 files, got {len(saved)}")
        return False


def test_streamlit_multifile():
    """Test realistic Streamlit multi-file project"""
    print("\n" + "="*60)
    print("TEST: Streamlit Multi-File Project")
    print("="*60)
    
    orchestrator = SimpleOrchestrator()
    
    response = """### FILENAME: streamlit_app.py
import streamlit as st
from database import TodoDatabase
from ui import render_todo_list

st.title("Todo App")

db = TodoDatabase()
todos = db.get_all()

render_todo_list(todos)

### FILENAME: database.py
class TodoDatabase:
    def __init__(self):
        self.todos = []
    
    def add_todo(self, task):
        self.todos.append({"task": task, "done": False})
    
    def get_all(self):
        return self.todos

### FILENAME: ui.py
import streamlit as st

def render_todo_list(todos):
    for todo in todos:
        st.checkbox(todo["task"], value=todo["done"])
"""
    
    user_input = "create a todo app with streamlit using multiple files"
    
    print("\n📝 Creating Streamlit multi-file project...")
    saved = orchestrator.parse_and_save_files(response, user_input)
    
    print(f"\n✅ Created {len(saved)} files:")
    for filepath in saved:
        filename = filepath.split('\\')[-1].split('/')[-1]
        print(f"   • {filename}")
    
    # Check if main file is named appropriately
    filenames = [f.split('\\')[-1].split('/')[-1] for f in saved]
    
    if "streamlit_app.py" in filenames or "streamlit_app_1.py" in filenames:
        print("\n✅ Main file correctly named (streamlit_app.py)")
    
    if len(saved) == 3:
        print("✅ ALL 3 FILES CREATED!")
        return True
    else:
        print(f"⚠️  Expected 3 files, got {len(saved)}")
        return False


if __name__ == "__main__":
    print("\n🧪 TESTING MULTI-FILE PROJECT HANDLING")
    
    test1 = test_multifile_project()
    test2 = test_multifile_with_folders()
    test3 = test_streamlit_multifile()
    
    print("\n" + "="*60)
    if test1 and test2 and test3:
        print("✅ ALL MULTI-FILE TESTS PASSED!")
        print("\n🎉 System handles:")
        print("   • Multiple files in one response")
        print("   • Files with folder structure")
        print("   • Framework-specific multi-file projects")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("="*60)
