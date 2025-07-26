#!/usr/bin/env python3
"""
Debug FastAPI startup issues
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

def test_imports():
    """Test all imports one by one"""
    print("🔍 Testing FastAPI Application Imports...")
    
    try:
        print("   Testing FastAPI...")
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
        print("   ✅ FastAPI imports working")
    except Exception as e:
        print(f"   ❌ FastAPI import error: {e}")
        return False
    
    try:
        print("   Testing Agent Orchestrator...")
        from agent.orchestrator import FinancialForecastingAgent
        print("   ✅ Agent imports working")
    except Exception as e:
        print(f"   ❌ Agent import error: {e}")
        return False
    
    try:
        print("   Testing Database...")
        from app.database import log_request_response, init_database
        print("   ✅ Database imports working")
    except Exception as e:
        print(f"   ❌ Database import error: {e}")
        print(f"   📝 Creating simplified database module...")
        return False
    
    return True

def test_agent_creation():
    """Test agent initialization"""
    print("\n🤖 Testing Agent Creation...")
    
    try:
        from agent.orchestrator import FinancialForecastingAgent
        agent = FinancialForecastingAgent()
        print("   ✅ Agent created successfully")
        return True
    except Exception as e:
        print(f"   ❌ Agent creation failed: {e}")
        return False

def test_basic_fastapi():
    """Test basic FastAPI app creation"""
    print("\n🚀 Testing Basic FastAPI App...")
    
    try:
        from fastapi import FastAPI
        app = FastAPI(title="Test App")
        
        @app.get("/")
        def root():
            return {"message": "test"}
        
        print("   ✅ Basic FastAPI app created")
        return True
    except Exception as e:
        print(f"   ❌ FastAPI app creation failed: {e}")
        return False

def main():
    """Debug FastAPI startup"""
    print("🔧 FASTAPI STARTUP DEBUGGING")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Agent Creation", test_agent_creation), 
        ("Basic FastAPI", test_basic_fastapi)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        success = test_func()
        if not success:
            print(f"\n❌ {test_name} failed - this is likely the issue")
            break
    else:
        print(f"\n✅ All basic tests passed - trying manual uvicorn start...")
        print(f"\nTry running manually:")
        print(f"   uvicorn app.main:app --reload --log-level debug")

if __name__ == "__main__":
    main()
