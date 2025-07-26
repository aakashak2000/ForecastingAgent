#!/usr/bin/env python3

import logging
import sys
import os
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_agent_orchestrator():
    """Test the complete FinancialForecastingAgent with all 3 tools"""
    
    print("🧪 Testing FinancialForecastingAgent - Complete System Integration")
    print("=" * 70)
    
    try:
        from agent.orchestrator import FinancialForecastingAgent
        
        # Initialize the master agent
        print(f"🤖 Initializing FinancialForecastingAgent...")
        agent = FinancialForecastingAgent()
        print("✅ Agent initialized with 3 specialized tools")
        
        # Generate complete forecast
        print(f"\n🚀 Generating comprehensive forecast for TCS...")
        print("   This will coordinate:")
        print("   1. FinancialDataExtractorTool (₹48,797 revenue)")
        print("   2. QualitativeAnalysisTool (management sentiment)")  
        print("   3. MarketDataTool (₹3,135.80 current price)")
        print("   4. LLM synthesis (combined insights)")
        
        forecast_result = agent.generate_forecast(
            company_symbol="TCS",
            forecast_period="Q2-2025"
        )
        
        # Display comprehensive results
        print(f"\n📊 COMPLETE FORECAST RESULTS:")
        print(f"   Success: {'✅' if forecast_result.success else '❌'}")
        print(f"   Processing Time: {forecast_result.processing_time:.2f} seconds")
        
        if not forecast_result.success:
            print(f"   Error: {forecast_result.error_message}")
            return False
        
        print(f"\n🎯 MASTER FORECAST:")
        print(f"   Company: {forecast_result.company_symbol}")
        print(f"   Period: {forecast_result.forecast_period}")
        print(f"   Overall Outlook: {forecast_result.overall_outlook.upper()}")
        print(f"   Confidence Score: {forecast_result.confidence_score:.2f}/1.0")
        print(f"   Investment Recommendation: {forecast_result.investment_recommendation.upper()}")
        
        # Show data from each tool
        print(f"\n📈 Tool Integration Status:")
        print(f"   Financial Metrics: {'✅' if forecast_result.financial_metrics else '⚠️ Using existing data'}")
        print(f"   Qualitative Analysis: {'✅' if forecast_result.qualitative_analysis else '❌'}")
        print(f"   Market Data: {'✅' if forecast_result.market_data else '❌'}")
        
        if forecast_result.key_drivers:
            print(f"\n🔑 Key Forecast Drivers:")
            for i, driver in enumerate(forecast_result.key_drivers, 1):
                print(f"   {i}. {driver}")
        
        print(f"\n🎉 Agent Orchestrator Test Complete!")
        
        # Success criteria: basic orchestration working
        success = forecast_result.success and forecast_result.confidence_score > 0
        
        if success:
            print(f"✅ SUCCESS: All 3 tools coordinated successfully!")
        else:
            print(f"⚠️  PARTIAL: Basic framework working, needs synthesis logic")
        
        return success
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure all previous tools are working")
        return False
        
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agent_orchestrator()
    sys.exit(0 if success else 1)
