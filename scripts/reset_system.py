#!/usr/bin/env python3
"""
Complete system reset - removes all cache, temporary files, databases
Use this to test fresh installation experience
"""

import os
import shutil
import glob
import subprocess
from pathlib import Path

def remove_directory(path, description):
    """Remove directory if it exists"""
    if Path(path).exists():
        shutil.rmtree(path)
        print(f"   ✅ Removed {description}: {path}")
    else:
        print(f"   ⚪ {description} not found: {path}")

def remove_file(path, description):
    """Remove file if it exists"""
    if Path(path).exists():
        os.remove(path)
        print(f"   ✅ Removed {description}: {path}")
    else:
        print(f"   ⚪ {description} not found: {path}")

def remove_pattern(pattern, description):
    """Remove files matching pattern"""
    files = glob.glob(pattern)
    if files:
        for file in files:
            os.remove(file)
        print(f"   ✅ Removed {len(files)} {description} files")
    else:
        print(f"   ⚪ No {description} files found")

def clear_mysql_database():
    """Clear MySQL database if it exists"""
    try:
        # Try to drop the database
        cmd = 'mysql -u root -e "DROP DATABASE IF EXISTS financial_forecasting;" 2>/dev/null'
        result = subprocess.run(cmd, shell=True, capture_output=True)
        if result.returncode == 0:
            print("   ✅ Cleared MySQL database")
        else:
            print("   ⚪ MySQL database not accessible or doesn't exist")
    except Exception as e:
        print(f"   ⚪ MySQL cleanup skipped: {e}")

def clear_python_cache():
    """Clear Python cache files"""
    cache_patterns = [
        "**/__pycache__",
        "**/*.pyc", 
        "**/*.pyo",
        "**/*.pyd",
        ".pytest_cache"
    ]
    
    for pattern in cache_patterns:
        for path in Path(".").rglob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    
    print("   ✅ Cleared Python cache files")

def main():
    """Complete system reset"""
    print("🧹 COMPLETE SYSTEM RESET")
    print("=" * 50)
    print("This will remove ALL cached data, databases, temporary files")
    print("Use this to test fresh installation experience")
    print("=" * 50)
    
    # Confirm reset
    response = input("Are you sure you want to reset everything? (y/N): ")
    if response.lower() != 'y':
        print("Reset cancelled")
        return
    
    print("\n🗑️  Removing Data Directories...")
    remove_directory("data", "Data directory")
    remove_directory("temp", "Temp directory") 
    remove_directory("vector_store_data", "Vector store data")
    remove_directory("test_vectorstore_data", "Test vector store")
    
    print("\n🗑️  Removing Temporary Files...")
    remove_pattern("*.db", "SQLite database")
    remove_pattern("*.sqlite", "SQLite")
    remove_pattern("*.sqlite3", "SQLite3")
    remove_pattern("temp_downloads/*", "Temp downloads")
    remove_pattern("/tmp/*TCS*.pdf", "Temp PDF files")
    remove_pattern("/var/folders/*/T/*TCS*.pdf", "System temp PDFs")
    
    print("\n🗑️  Removing Test Output Files...")
    remove_pattern("test_*_results.json", "Test result")
    remove_pattern("business_forecast_output.json", "Business forecast")
    remove_pattern("manual_transcript_extraction.txt", "Manual extraction")
    
    print("\n🗑️  Removing Environment Files...")
    remove_file(".env", "Environment configuration")
    
    print("\n🗑️  Clearing Python Cache...")
    clear_python_cache()
    
    print("\n🗑️  Clearing MySQL Database...")
    clear_mysql_database()
    
    print("\n🧹 RESET COMPLETE!")
    print("=" * 50)
    print("✅ System is now in completely fresh state")
    print("✅ Ready to test fresh installation experience")
    print("")
    print("🚀 Next steps:")
    print("1. Run: python setup.py")
    print("2. Run: uvicorn app.main:app --reload")
    print("3. Test: curl -X POST 'http://localhost:8000/forecast' \\")
    print("         -H 'Content-Type: application/json' \\")
    print("         -d '{\"company_symbol\": \"TCS\"}'")

if __name__ == "__main__":
    main()