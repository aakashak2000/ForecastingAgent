#!/usr/bin/env python3
"""
Quick setup script for Financial Forecasting Agent
Handles: dependencies, directories, ollama setup, data download
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def run_command(cmd, description):
    """Run command with error handling"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def setup_system():
    """Complete system setup"""
    print("🚀 Financial Forecasting Agent - Quick Setup")
    print("=" * 50)
    
    # 1. Install Python dependencies
    print("\n📦 Installing dependencies...")
    if not run_command("pip install -r requirements.txt", "Python dependencies"):
        return False
    
    # 2. Create directories
    print("\n📁 Creating directories...")
    directories = ["data/downloads", "data/vector_store", "data/logs"]
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✅ Directories created")
    
    # 3. Setup Ollama (if available)
    print("\n🤖 Setting up Ollama...")
    if run_command("ollama --version", "Check Ollama installation"):
        run_command("ollama pull llama3.1:8b", "Download LLM model")
    else:
        print("⚠️  Ollama not installed - will use other LLM providers")
    
    # 4. Test LLM connectivity
    print("\n🧪 Testing LLM connectivity...")
    if not run_command("python tests/test_llm_manager.py", "LLM Manager test"):
        print("⚠️  LLM test failed - check API keys in .env file")
    
    print("\n🎉 Setup completed! Ready to test.")
    return True

if __name__ == "__main__":
    success = setup_system()
    
    if success:
        print("\n🚀 NEXT STEPS:")
        print("1. Run: python scripts/test_complete_system.py    # System health check")
        print("2. Run: python scripts/test_business_forecast.py  # Business report")  
        print("3. Run: uvicorn app.main:app --reload              # Start API server")
        sys.exit(0)
    else:
        print("\n❌ Setup failed - check errors above")
        sys.exit(1)