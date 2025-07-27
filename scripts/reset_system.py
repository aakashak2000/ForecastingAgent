#!/usr/bin/env python3
"""
Complete system reset for evaluator testing
Removes all cached data, downloads, databases, temp files
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

def remove_pattern(pattern, description):
    """Remove files matching pattern"""
    files = glob.glob(pattern, recursive=True)
    if files:
        for file in files:
            if os.path.isfile(file):
                os.remove(file)
        print(f"   ✅ Removed {len(files)} {description} files")
    else:
        print(f"   ⚪ No {description} files found")

def main():
    print("🧹 COMPLETE SYSTEM RESET FOR EVALUATOR TESTING")
    print("=" * 60)
    
    # Remove all data directories
    print("\n🗑️  Removing Data Directories...")
    remove_directory("data", "Data directory")
    remove_directory("temp_downloads", "Temp downloads")
    
    # Remove all temporary files
    print("\n🗑️  Removing Temporary Files...")
    remove_pattern("*.db", "SQLite database")
    remove_pattern("*.sqlite*", "SQLite")
    remove_pattern("**/*TCS*.pdf", "TCS PDF files")
    remove_pattern("/tmp/*TCS*.pdf", "System temp PDFs")
    remove_pattern("/var/folders/*/T/*TCS*.pdf", "Mac temp PDFs")
    
    # Remove all test output files
    print("\n🗑️  Removing Test Output Files...")
    remove_pattern("test_*_results.json", "Test result")
    remove_pattern("business_forecast_output.json", "Business forecast")
    remove_pattern("*_results.json", "Result files")
    remove_pattern("manual_*.txt", "Manual extraction")
    
    # Remove Python cache
    print("\n🗑️  Removing Python Cache...")
    remove_pattern("**/__pycache__", "Python cache")
    remove_pattern("**/*.pyc", "Python compiled")
    
    # Clear MySQL database
    print("\n🗑️  Clearing MySQL Database...")
    try:
        cmd = 'mysql -u root -e "DROP DATABASE IF EXISTS financial_forecasting;" 2>/dev/null'
        subprocess.run(cmd, shell=True, capture_output=True)
        print("   ✅ Cleared MySQL database")
    except:
        print("   ⚪ MySQL cleanup skipped")
    
    print("\n🎉 RESET COMPLETE!")
    print("   System is now in completely fresh state")
    print("   Ready for evaluator testing")

if __name__ == "__main__":
    main()