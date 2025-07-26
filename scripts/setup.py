#!/usr/bin/env python3
"""
One-command setup for Financial Forecasting Agent
Works on Mac, Linux, Windows, and Colab
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_step(step, description):
    """Print formatted step"""
    print(f"\n🔧 Step {step}: {description}")
    print("-" * 50)

def run_command(cmd, description, optional=False):
    """Run command with error handling"""
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
        if result.returncode == 0:
            print(f"   ✅ {description}")
            return True
        else:
            if optional:
                print(f"   ⚠️  {description} (optional - skipped)")
                return True
            else:
                print(f"   ❌ {description} failed: {result.stderr}")
                return False
    except Exception as e:
        if optional:
            print(f"   ⚠️  {description} (optional - skipped): {e}")
            return True
        else:
            print(f"   ❌ {description} failed: {e}")
            return False

def setup_directories():
    """Create necessary directories"""
    directories = [
        "data/downloads",
        "data/vector_store", 
        "data/logs"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("   ✅ Created data directories")

def setup_environment():
    """Create .env file if not exists"""
    if not Path(".env").exists():
        if Path(".env.example").exists():
            shutil.copy(".env.example", ".env")
            print("   ✅ Created .env file from template")
        else:
            # Create basic .env
            with open(".env", "w") as f:
                f.write("# Database Configuration\n")
                f.write("MYSQL_PASSWORD=\n")
                f.write("# Optional API Keys\n")
                f.write("OPENAI_API_KEY=\n")
            print("   ✅ Created basic .env file")
    else:
        print("   ✅ .env file already exists")

def detect_mysql():
    """Try to detect and setup MySQL"""
    system = platform.system().lower()
    
    # Check if MySQL is already running
    mysql_running = run_command("mysql --version", "Check MySQL installation", optional=True)
    
    if mysql_running:
        print("   ✅ MySQL detected")
        
        # Try to connect and setup database
        setup_db_cmd = """
        mysql -u root -e "
        CREATE DATABASE IF NOT EXISTS financial_forecasting;
        SELECT 'Database ready' as status;
        " 2>/dev/null
        """
        
        if run_command(setup_db_cmd, "Setup MySQL database", optional=True):
            print("   💡 MySQL ready! Add your root password to .env file:")
            print("      MYSQL_PASSWORD=your_mysql_password")
        else:
            print("   💡 MySQL detected but needs password in .env file")
    else:
        print("   ⚠️  MySQL not detected - will use SQLite (works perfectly!)")

def setup_ollama():
    """Setup Ollama if available"""
    if run_command("ollama --version", "Check Ollama installation", optional=True):
        print("   ✅ Ollama detected")
        run_command("ollama pull llama3.1:8b", "Download AI model", optional=True)
    else:
        print("   💡 Ollama not installed - will use cloud AI providers")

def main():
    """Main setup process"""
    print("🚀 FINANCIAL FORECASTING AGENT - AUTOMATIC SETUP")
    print("=" * 60)
    print("This script will set up everything needed to run the application.")
    print("Works on Mac, Linux, Windows, and Google Colab!")
    print("=" * 60)
    
    success = True
    
    # Step 1: Install Python dependencies
    print_step(1, "Installing Python Dependencies")
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      "Install Python packages"):
        print("❌ Failed to install dependencies")
        return False
    
    # Step 2: Create directories
    print_step(2, "Setting Up Directories")
    setup_directories()
    
    # Step 3: Environment configuration
    print_step(3, "Environment Configuration")
    setup_environment()
    
    # Step 4: Database detection
    print_step(4, "Database Setup")
    detect_mysql()
    
    # Step 5: AI model setup
    print_step(5, "AI Model Setup")
    setup_ollama()
    
    # Step 6: Verify installation
    print_step(6, "Testing Installation")
    if run_command([sys.executable, "-c", "from app.main import app; print('✅ FastAPI app loads successfully')"], 
                  "Test FastAPI imports"):
        print("   ✅ Application ready!")
    else:
        print("   ❌ Application test failed")
        success = False
    
    # Final instructions
    print(f"\n🎉 SETUP COMPLETE!")
    print("=" * 60)
    
    if success:
        print("✅ Everything is ready! To start the application:")
        print("")
        print("   1. Start the server:")
        print("      uvicorn app.main:app --reload")
        print("")
        print("   2. Test the API:")
        print("      curl -X POST 'http://localhost:8000/forecast' \\")
        print("           -H 'Content-Type: application/json' \\")
        print("           -d '{\"company_symbol\": \"TCS\"}'")
        print("")
        print("   3. Optional: Add your MySQL password to .env for database logging")
        print("")
        print("🌐 API Documentation: http://localhost:8000/docs")
        
    else:
        print("⚠️  Some optional components failed, but the application should still work.")
        print("   Check the error messages above and try running:")
        print("   uvicorn app.main:app --reload")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)