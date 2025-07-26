#!/usr/bin/env python3
"""
Complete end-to-end system test for Financial Forecasting Agent
Tests: LLM → Data Download → Vector Store → Financial Extraction → Market Data → Agent Orchestrator
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise during testing

def test_component(component_name, test_function):
    """Test individual component with timing"""
    print(f"\n🧪 Testing {component_name}...")
    print("-" * 40)
    
    start_time = time.time()
    try:
        success = test_function()
        duration = time.time() - start_time
        
        if success:
            print(f"✅ {component_name}: PASSED ({duration:.1f}s)")
            return True
        else:
            print(f"❌ {component_name}: FAILED ({duration:.1f}s)")
            return False
            
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ {component_name}: ERROR - {e} ({duration:.1f}s)")
        return False

def test_llm_manager():
    """Test LLM connectivity"""
    try:
        from app.llm_manager import LLMProviderManager
        manager = LLMProviderManager()
        llm = manager.get_llm()
        response = llm.invoke("Hello")
        print(f"   LLM Provider: {manager.current_provider}")
        print(f"   Test Response: {str(response)[:50]}...")
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_data_downloader():
    """Test document download and transcript extraction"""
    try:
        from utils.data_downloader import ScreenerDataDownloader
        downloader = ScreenerDataDownloader()
        
        # Test document discovery
        documents = downloader.get_company_documents("TCS")
        print(f"   Annual Reports Found: {len(documents['annual_reports'])}")
        print(f"   Concalls Found: {len(documents['concalls'])}")
        
        # Test downloading (limit to 1 to save time)
        if documents['concalls']:
            transcript_url = documents['concalls'][0].get('transcript_url')
            if transcript_url:
                content = downloader.extract_transcript_content(transcript_url)
                if content and len(content) > 1000:
                    print(f"   Transcript Extracted: {len(content)} characters")
                    return True
        
        print("   No usable transcript content found")
        return False
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_vector_store():
    """Test vector store and transcript processing"""
    try:
        from vector_store.transcript_vectorstore import TranscriptVectorStore
        vectorstore = TranscriptVectorStore(persist_directory="data/vector_store")
        
        # Check if data exists or add sample
        stats = vectorstore.get_collection_stats()
        if stats.get('total_chunks', 0) == 0:
            # Add sample transcript data
            sample_transcript = """
            CEO: We are pleased to report strong financial performance this quarter. 
            Our revenue growth of 12% demonstrates solid execution of our strategy.
            We continue to invest in AI and cloud technologies for future growth.
            Analyst: What are your expectations for the next quarter?
            CEO: We expect continued growth driven by digital transformation demand.
            """
            chunks_added = vectorstore.add_transcript(
                sample_transcript, "TCS", "Q1-2025", {"source": "test"}
            )
            print(f"   Added {chunks_added} sample chunks")
        
        # Test search functionality
        results = vectorstore.search_transcripts("growth outlook", "TCS", n_results=3)
        print(f"   Search Results: {len(results)} chunks found")
        print(f"   Total Chunks: {stats.get('total_chunks', 0)}")
        
        return len(results) > 0 or stats.get('total_chunks', 0) > 0
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_market_data():
    """Test live market data fetching"""
    try:
        from tools.market_data import MarketDataTool
        tool = MarketDataTool()
        
        market_data = tool.get_stock_data("TCS")
        if market_data:
            print(f"   TCS Price: ₹{market_data.current_price:,.2f}")
            print(f"   P/E Ratio: {market_data.pe_ratio}")
            
            # Test market context
            context = tool.analyze_market_context(market_data)
            if context:
                print(f"   Valuation: {context.current_valuation}")
                print(f"   Risk Level: {context.risk_level}")
                return True
        
        return False
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_qualitative_analyzer():
    """Test qualitative analysis tool"""
    try:
        from tools.qualitative_analyzer import QualitativeAnalysisTool
        analyzer = QualitativeAnalysisTool(vectorstore_dir="data/vector_store")
        
        result = analyzer.analyze_transcripts("TCS", "Q1-2025")
        if result.success:
            print(f"   Total Insights: {result.total_insights}")
            print(f"   Confidence: {result.average_confidence:.2f}")
            print(f"   Sentiment: {result.management_sentiment.overall_tone}")
            return True
        else:
            print(f"   Analysis failed: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_agent_orchestrator():
    """Test complete agent orchestration"""
    try:
        from agent.orchestrator import FinancialForecastingAgent
        agent = FinancialForecastingAgent()
        
        result = agent.generate_forecast("TCS", "Q2-2025")
        if result.success:
            print(f"   Forecast: {result.overall_outlook.upper()}")
            print(f"   Confidence: {result.confidence_score:.2f}")
            print(f"   Recommendation: {result.investment_recommendation.upper()}")
            print(f"   Processing Time: {result.processing_time:.1f}s")
            print(f"   Key Drivers: {len(result.key_drivers)}")
            return True
        else:
            print(f"   Forecast failed: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"   Error: {e}")
        return False

def main():
    """Run complete system test"""
    print("🎯 FINANCIAL FORECASTING AGENT - COMPLETE SYSTEM TEST")
    print("=" * 60)
    
    # Test components in dependency order
    tests = [
        ("LLM Manager", test_llm_manager),
        ("Data Downloader", test_data_downloader),
        ("Vector Store", test_vector_store),
        ("Market Data Tool", test_market_data),
        ("Qualitative Analyzer", test_qualitative_analyzer),
        ("Agent Orchestrator", test_agent_orchestrator)
    ]
    
    results = {}
    total_start = time.time()
    
    for component_name, test_func in tests:
        results[component_name] = test_component(component_name, test_func)
    
    # Final summary
    total_time = time.time() - total_start
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n🏆 FINAL RESULTS")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {passed/total*100:.0f}%")
    print(f"Total Time: {total_time:.1f}s")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! System is fully operational.")
        print(f"🚀 Ready for production deployment!")
        return True
    else:
        print(f"\n⚠️  Some components need attention. Check failed tests above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)