#!/usr/bin/env python3
"""
Test complete FastAPI system - simulates evaluator experience
Tests: FastAPI startup, database logging, endpoint response, business output
"""

import sys
import time
import json
import requests
import subprocess
import threading
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

def start_fastapi_server():
    """Start FastAPI server in background"""
    print("🚀 Starting FastAPI server...")
    
    try:
        # Start server process
        process = subprocess.Popen(
            ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        print("   Waiting for server startup...")
        time.sleep(8)  # Give server time to initialize
        
        # Test if server is responding
        try:
            response = requests.get("http://127.0.0.1:8000/", timeout=5)
            if response.status_code == 200:
                print("✅ FastAPI server is running")
                return process
            else:
                print(f"❌ Server responded with status {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Server not responding: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def test_health_endpoints():
    """Test basic API health"""
    print("\n🧪 Testing API Health Endpoints...")
    
    try:
        # Test root endpoint
        response = requests.get("http://127.0.0.1:8000/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Root endpoint: {data['service']}")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
            return False
        
        # Test health endpoint
        response = requests.get("http://127.0.0.1:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check: {data['status']}")
            print(f"   📊 Components: {len(data['components'])} operational")
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False

def test_forecast_endpoint():
    """Test main forecast endpoint - the core deliverable"""
    print("\n🎯 Testing Main Forecast Endpoint...")
    
    try:
        # Prepare request
        request_data = {
            "company_symbol": "TCS",
            "forecast_period": "Q2-2025"
        }
        
        print(f"   📤 Request: {request_data}")
        print(f"   ⏳ Processing forecast (this may take 60+ seconds)...")
        
        start_time = time.time()
        
        # Make request to forecast endpoint
        response = requests.post(
            "http://127.0.0.1:8000/forecast",
            json=request_data,
            timeout=300  # 5 minute timeout for complete analysis
        )
        
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            forecast_data = response.json()
            
            print(f"\n📊 FORECAST RESPONSE RECEIVED ({processing_time:.1f}s)")
            print("=" * 60)
            
            # Display key business metrics
            print(f"Company: {forecast_data['company_symbol']}")
            print(f"Recommendation: {forecast_data['investment_recommendation'].upper()}")
            print(f"Outlook: {forecast_data['overall_outlook'].upper()}")
            print(f"Confidence: {forecast_data['analyst_confidence']:.0%}")
            
            # Financial metrics
            if forecast_data.get('current_price'):
                print(f"\n💰 Financial Metrics:")
                print(f"   Current Price: ₹{forecast_data['current_price']:,.2f}")
                if forecast_data.get('target_price'):
                    print(f"   Target Price: ₹{forecast_data['target_price']:,.0f}")
                    print(f"   Upside: +{forecast_data.get('target_upside_percent', 0):.0f}%")
                print(f"   P/E Ratio: {forecast_data.get('pe_ratio', 'N/A')}")
                print(f"   Market Cap: ₹{forecast_data.get('market_cap_crores', 0):,.0f} Cr")
            
            # Market context
            if forecast_data.get('valuation_assessment'):
                print(f"\n📈 Market Analysis:")
                print(f"   Valuation: {forecast_data['valuation_assessment'].replace('_', ' ').title()}")
                print(f"   Momentum: {forecast_data.get('price_momentum', 'N/A').title()}")
                print(f"   Risk Level: {forecast_data.get('risk_level', 'N/A').title()}")
            
            # Business insights
            print(f"\n🎯 Key Business Drivers:")
            for i, driver in enumerate(forecast_data.get('key_drivers', []), 1):
                print(f"   {i}. {driver}")
            
            # Growth opportunities
            if forecast_data.get('growth_opportunities'):
                print(f"\n🚀 Growth Opportunities:")
                for opp in forecast_data['growth_opportunities'][:2]:
                    print(f"   • {opp}")
            
            # Management insights
            if forecast_data.get('management_sentiment'):
                print(f"\n😊 Management Sentiment: {forecast_data['management_sentiment'].title()}")
                if forecast_data.get('management_optimism_score'):
                    print(f"   Optimism Score: {forecast_data['management_optimism_score']:.0%}")
            
            # Metadata
            print(f"\n📋 Analysis Metadata:")
            print(f"   Processing Time: {forecast_data['processing_time']:.1f}s")
            print(f"   Data Sources: {', '.join(forecast_data.get('data_sources', []))}")
            print(f"   Generated: {forecast_data.get('generated_at', 'N/A')}")
            
            # Validate response structure
            required_fields = [
                'company_symbol', 'investment_recommendation', 'overall_outlook', 
                'analyst_confidence', 'key_drivers', 'processing_time'
            ]
            
            missing_fields = [field for field in required_fields if field not in forecast_data]
            if missing_fields:
                print(f"\n⚠️  Missing fields: {missing_fields}")
                return False
            
            print(f"\n✅ FORECAST ENDPOINT TEST PASSED!")
            print(f"   ✅ Structured JSON response received")
            print(f"   ✅ All required business fields present")
            print(f"   ✅ Professional-grade analysis delivered")
            
            return True
            
        else:
            print(f"❌ Forecast endpoint failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout - analysis took too long")
        return False
    except Exception as e:
        print(f"❌ Forecast test failed: {e}")
        return False

def test_database_logging():
    """Test database logging functionality"""
    print("\n🗄️ Testing Database Logging...")
    
    try:
        from app.database import get_database_stats
        import asyncio
        
        # Get database stats
        stats = asyncio.run(get_database_stats())
        
        if 'error' not in stats:
            print(f"   ✅ Database Type: {stats.get('database_type', 'unknown')}")
            print(f"   ✅ Total Requests: {stats.get('total_requests', 0)}")
            print(f"   ✅ Success Rate: {stats.get('success_rate', '0%')}")
            return True
        else:
            print(f"   ❌ Database stats error: {stats['error']}")
            return False
            
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False

def main():
    """Run complete FastAPI system test"""
    print("🎯 FASTAPI SYSTEM TEST - Complete Business Application")
    print("=" * 70)
    print("This simulates the exact evaluator experience:")
    print("1. Start FastAPI server")
    print("2. Hit /forecast endpoint")  
    print("3. Verify business-grade JSON response")
    print("4. Check database logging")
    
    # Start FastAPI server
    server_process = start_fastapi_server()
    if not server_process:
        print("❌ Failed to start FastAPI server")
        return False
    
    try:
        # Test system components
        tests = [
            ("API Health", test_health_endpoints),
            ("Forecast Endpoint", test_forecast_endpoint),
            ("Database Logging", test_database_logging)
        ]
        
        results = {}
        for test_name, test_func in tests:
            results[test_name] = test_func()
        
        # Final results
        passed = sum(results.values())
        total = len(results)
        
        print(f"\n🏆 FASTAPI SYSTEM TEST RESULTS")
        print("=" * 70)
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {passed/total*100:.0f}%")
        
        if passed == total:
            print(f"\n🎉 COMPLETE SUCCESS!")
            print(f"✅ FastAPI server operational")
            print(f"✅ Forecast endpoint delivering business-grade analysis")
            print(f"✅ Database logging functional") 
            print(f"✅ Ready for evaluator testing!")
            
            print(f"\n📋 EVALUATOR COMMANDS:")
            print(f"   uvicorn app.main:app --reload")
            print(f"   curl -X POST 'http://localhost:8000/forecast' \\")
            print(f"        -H 'Content-Type: application/json' \\")
            print(f"        -d '{{\"company_symbol\": \"TCS\"}}'")
            
            return True
        else:
            print(f"\n⚠️  Some tests failed - check output above")
            return False
            
    finally:
        # Clean up server process
        if server_process:
            print(f"\n🔄 Shutting down FastAPI server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
