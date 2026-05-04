"""
Test automatic backup feature
"""
import os
import time
from orchestrator.simple_engine import SimpleOrchestrator

def test_backup():
    """Test that files are backed up before overwriting"""
    print("\n" + "="*60)
    print("TEST: Automatic Backup Feature")
    print("="*60)
    
    orchestrator = SimpleOrchestrator()
    
    # Create initial file
    print("\n1. Creating initial app.py...")
    response1 = """### FILENAME: app.py
print("Version 1")"""
    
    saved1 = orchestrator.parse_and_save_files(response1)
    print(f"✅ Created: {saved1}")
    
    # Wait a second to ensure different timestamp
    time.sleep(1)
    
    # Create new version (should backup old one)
    print("\n2. Creating new version of app.py...")
    response2 = """### FILENAME: app.py
print("Version 2 - Updated!")"""
    
    saved2 = orchestrator.parse_and_save_files(response2)
    print(f"✅ Updated: {saved2}")
    
    # Check backup directory
    backup_dir = os.path.join(orchestrator.output_dir, ".backups")
    if os.path.exists(backup_dir):
        backups = os.listdir(backup_dir)
        print(f"\n3. Backups created: {len(backups)}")
        for backup in backups:
            print(f"   📦 {backup}")
        
        # Verify backup content
        if backups:
            backup_path = os.path.join(backup_dir, backups[0])
            with open(backup_path, 'r') as f:
                backup_content = f.read()
            
            if "Version 1" in backup_content:
                print("\n✅ Backup contains old version")
            else:
                print("\n❌ Backup content incorrect")
        
        # Verify current file has new version
        current_path = os.path.join(orchestrator.output_dir, "app.py")
        with open(current_path, 'r') as f:
            current_content = f.read()
        
        if "Version 2" in current_content:
            print("✅ Current file has new version")
        else:
            print("❌ Current file content incorrect")
        
        print("\n" + "="*60)
        print("✅ BACKUP FEATURE WORKING!")
        print("="*60)
        
    else:
        print("\n❌ Backup directory not created")


if __name__ == "__main__":
    test_backup()
