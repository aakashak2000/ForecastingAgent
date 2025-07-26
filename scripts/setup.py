#!/usr/bin/env python3
"""
Setup script for Financial Forecasting Agent
"""

import os
import subprocess
import sys
from pathlib import Path

def setup_directories():
    """Create necessary directories"""
    dirs = [
        "data/downloads",
        "data/vector_store", 
        "data/logs",
        "temp"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")

def install_dependencies():
    """Install Python dependencies"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False
    return True

def setup_ollama():
    """Setup Ollama if available"""
    try:
        subprocess.check_call(["ollama", "pull", "llama3.1:8b"])
        print("✅ Ollama model downloaded")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Ollama not available - will use other LLM providers")

def main():
    print("🚀 Setting up Financial Forecasting Agent")
    print("=" * 50)
    
    setup_directories()
    
    if install_dependencies():
        setup_ollama()
        
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your API keys")
        print("2. Run: python tests/test_llm_manager.py")
        print("3. Run: python tests/test_data_downloader.py") 
        print("4. Start the FastAPI server: uvicorn app.main:app --reload")
    else:
        print("\n❌ Setup failed - check dependencies")

if __name__ == "__main__":
    main()