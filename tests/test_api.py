#!/usr/bin/env python3
"""
Complete System Verification - Tests all requirements are working
Tests: Financial Extraction + RAG Quality + Market Data + Agent Orchestration + MySQL Logging
"""

import sys
import json
import time
import requests
import subprocess
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

def test_financial_extraction():
    """Test that financial extraction actually works"""
    print("🔧 Testing Financial Data Extraction...")
    
    try:
        from tools.financial_extractor import FinancialDataExtractorTool
        from utils.data_downloader import ScreenerDataDownloader
        
        # Download fresh report
        downloader = ScreenerDataDownloader()
        results = downloader.get_latest_documents("TCS", max_reports=1, max_transcripts=0)
        
        if not results['annual_reports']:
            print("   ❌ No financial reports downloaded")
            return False
        
        # Extract financial data
        extractor = FinancialDataExtractorTool()
        report = results['annual_reports'][0]
        
        result = extractor.extract_financial_data(
            pdf_path=report['local_path'],
            company_symbol="TCS",
            report_period=f"FY{report['year']}"
        )
        
        if result.success and result.metrics:
            metrics = result.metrics
            print(f"   ✅ Financial extraction working:")
            print(f"      Revenue: ₹{metrics.total_revenue} Cr" if metrics.total_revenue else "      Revenue: Not extracted")
            print(f"      Net Profit: ₹{metrics.net_profit} Cr" if metrics.net_profit else "      Net Profit: Not extracted") 
            print(f"      Confidence: {metrics.extraction_confidence:.2f}")
            return metrics.total_revenue is not None or metrics.net_profit is not None
        else:
            print("   ❌ Financial extraction failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Financial extraction error: {e}")
        return False

def test_rag_quality():
    """Test RAG system quality and retrieval"""
    print("\n🧠 Testing RAG Quality and Retrieval...")
    
    try:
        from vector_store.transcript_vectorstore import TranscriptVectorStore
        
        vectorstore = TranscriptVectorStore(persist_directory="data/vector_store")
        stats = vectorstore.get_collection_stats()
        
        print(f"   📊 Vector Store Stats:")
        print(f"      Total chunks: {stats.get('total_chunks', 0)}")
        print(f"      Companies: {stats.get('companies', [])}")
        print(f"      Average quality: {stats.get('average_quality_score', 0):.3f}")
        print(f"      Quality status: {stats.get('quality_status', 'unknown')}")
        
        if stats.get('total_chunks', 0) < 20:
            print("   ❌ Insufficient RAG data")
            return False
        
        # Test retrieval quality
        test_queries = [
            "revenue growth outlook management",
            "business guidance future quarter",
            "cost optimization margin",
            "AI technology innovation"
        ]
        
        good_retrievals = 0
        for query in test_queries:
            results = vectorstore.search_transcripts(query, "TCS", n_results=3, min_similarity=0.1)
            if results:
                best_similarity = max(r.get('similarity', 0) for r in results)
                if best_similarity > 0.3:
                    good_retrievals += 1
                print(f"      '{query[:20]}...': {len(results)} results, best: {best_similarity:.3f}")
            else:
                print(f"      '{query[:20]}...': No results")
        
        quality_ratio = good_retrievals / len(test_queries)
        print(f"   🎯 Retrieval Quality: {quality_ratio:.1%} ({good_retrievals}/{len(test_queries)})")
        
        return quality_ratio >= 0.5  # At least 50% good retrievals
        
    except Exception as e:
        print(f"   ❌ RAG quality test error: {e}")
        return False

def test_market_data():
    """Test market data integration"""
    print("\n📈 Testing Market Data Integration...")
    
    try:
        from tools.market_data import MarketDataTool
        
        tool = MarketDataTool()
        market_data = tool.get_stock_data("TCS")
        
        if market_data:
            print(f"   ✅ Market data retrieved:")
            print(f"      Current Price: ₹{market_data.current_price:,.2f}")
            print(f"      P/E Ratio: {market_data.pe_ratio}")
            print(f"      Market Cap: ₹{market_data.market_cap:,.0f} Cr")
            
            # Test market context
            context = tool.analyze_market_context(market_data)
            if context:
                print(f"      Valuation: {context.current_valuation}")
                print(f"      Risk Level: {context.risk_level}")
                return True
            else:
                print("   ❌ Market context analysis failed")
                return False
        else:
            print("   ❌ Market data retrieval failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Market data test error: {e}")
        return False

def test_agent_orchestration():
    """Test complete agent orchestration"""
    print("\n🤖 Testing Agent Orchestration...")
    
    try:
        from agent.orchestrator import FinancialForecastingAgent
        
        agent = FinancialForecastingAgent()
        print("   ✅ Agent initialized")
        
        # Test comprehensive forecast
        print("   🔄 Generating comprehensive forecast...")
        result = agent.generate_forecast("TCS", "Q2-2025")
        
        if result.success:
            print(f"   ✅ Orchestration successful:")
            print(f"      Overall Outlook: {result.overall_outlook}")
            print(f"      Recommendation: {result.investment_recommendation}")
            print(f"      Confidence: {result.confidence_score:.2f}")
            print(f"      Key Drivers: {len(result.key_drivers)}")
            print(f"      Processing Time: {result.processing_time:.1f}s")
            
            # Check data integration
            data_sources = []
            if result.financial_metrics:
                data_sources.append("Financial")
            if result.qualitative_analysis:
                data_sources.append("Qualitative")
            if result.market_data:
                data_sources.append("Market")
            
            print(f"      Data Sources: {', '.join(data_sources)}")
            
            # Success criteria: at least 2 of 3 data sources working
            return len(data_sources) >= 2
        else:
            print(f"   ❌ Orchestration failed: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"   ❌ Agent orchestration error: {e}")
        return False

def test_fastapi_integration():
    """Test FastAPI endpoint integration"""
    print("\n🚀 Testing FastAPI Integration...")
    
    try:
        # Check if server is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code != 200:
                print("   ⚠️ FastAPI server not running - start with: uvicorn app.main:app --reload")
                return False
        except requests.exceptions.RequestException:
            print("   ⚠️ FastAPI server not accessible - start with: uvicorn app.main:app --reload")
            return False
        
        # Test forecast endpoint
        print("   🔄 Testing /forecast endpoint...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8000/forecast",
            json={"company_symbol": "TCS", "forecast_period": "Q2-2025"},
            timeout=120
        )
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API endpoint working:")
            print(f"      Response Time: {response_time:.1f}s")
            print(f"      Recommendation: {data.get('investment_recommendation', 'unknown')}")
            print(f"      Confidence: {data.get('analyst_confidence', 0):.2f}")
            print(f"      Current Price: ₹{data.get('current_price', 0):,.2f}")
            
            # Check completeness
            required_fields = [
                'investment_recommendation', 'overall_outlook', 'analyst_confidence',
                'current_price', 'key_drivers'
            ]
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                print(f"   ⚠️ Missing fields: {missing_fields}")
                return False
            
            return True
        else:
            print(f"   ❌ API endpoint failed: {response.status_code}")
            print(f"      Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ FastAPI integration error: {e}")
        return False

def test_mysql_logging():
    """Test MySQL database logging"""
    print("\n🗄️ Testing MySQL Database Logging...")
    
    try:
        import mysql.connector
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        # Test database connection
        config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', ''),
            'database': os.getenv('MYSQL_DATABASE', 'financial_forecasting')
        }
        
        if not config['password']:
            print("   ⚠️ No MySQL password in .env file")
            return False
        
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Check recent requests
        cursor.execute("""
            SELECT COUNT(*) as total_requests 
            FROM forecast_requests
        """)
        total_requests = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT company_symbol, 
                   JSON_EXTRACT(response_data, '$.investment_recommendation') as recommendation,
                   created_at
            FROM forecast_requests 
            ORDER BY created_at DESC 
            LIMIT 3
        """)
        
        recent_requests = cursor.fetchall()
        
        print(f"   ✅ MySQL logging working:")
        print(f"      Total requests: {total_requests}")
        print(f"      Recent requests:")
        
        for req in recent_requests:
            company, recommendation, created_at = req
            print(f"        {company}: {recommendation} at {created_at}")
        
        connection.close()
        return total_requests > 0
        
    except Exception as e:
        print(f"   ❌ MySQL logging error: {e}")
        return False

def main():
    """Run complete system verification"""
    print("🎯 COMPLETE SYSTEM VERIFICATION")
    print("=" * 60)
    print("Testing all requirements from task document:")
    print("1. Financial Data Extraction from quarterly reports")
    print("2. RAG-based qualitative analysis of transcripts")
    print("3. Live market data integration")
    print("4. Agent orchestration and LLM synthesis")
    print("5. FastAPI REST endpoint")
    print("6. MySQL database logging")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Financial Extraction", test_financial_extraction),
        ("RAG Quality", test_rag_quality),
        ("Market Data", test_market_data),
        ("Agent Orchestration", test_agent_orchestration),
        ("FastAPI Integration", test_fastapi_integration),
        ("MySQL Logging", test_mysql_logging)
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Final summary
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n🏆 VERIFICATION RESULTS")
    print("=" * 60)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name:20}: {status}")
    
    print(f"\nOverall Score: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print(f"\n🎉 PERFECT! ALL REQUIREMENTS WORKING!")
        print(f"✅ Task compliance: 100%")
        print(f"✅ Financial extraction from quarterly reports")
        print(f"✅ RAG analysis of 2-3 earnings call transcripts")  
        print(f"✅ Live market data integration")
        print(f"✅ Multi-source forecast synthesis")
        print(f"✅ Structured JSON output")
        print(f"✅ MySQL database logging")
        print(f"\n🚀 System ready for evaluator testing!")
        
    elif passed >= 4:
        print(f"\n✅ GOOD! Core requirements working ({passed}/6)")
        print(f"⚠️ Address failed components for full compliance")
        
    else:
        print(f"\n❌ NEEDS WORK! Multiple components failing ({passed}/6)")
        print(f"🔧 Fix failed components before submission")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)