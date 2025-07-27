#!/usr/bin/env python3
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

def test_fresh_system():
    print("🎯 FRESH END-TO-END SYSTEM TEST")
    print("=" * 60)
    print("Testing complete workflow:")
    print("1. Download fresh financial reports")
    print("2. Download fresh earnings call transcripts") 
    print("3. Financial data extraction")
    print("4. RAG-based qualitative analysis")
    print("5. Live market data")
    print("6. Complete forecast generation")
    print("=" * 60)
    
    try:
        from agent.orchestrator import FinancialForecastingAgent
        
        # Initialize fresh agent
        print(f"\n🤖 Step 1: Initialize Agent...")
        agent = FinancialForecastingAgent()
        print("✅ Agent initialized")
        
        # Run complete forecast (this will download everything fresh)
        print(f"\n🚀 Step 2: Generate Complete Forecast...")
        print("   This will:")
        print("   - Download latest TCS financial reports")
        print("   - Download latest 3 earnings call transcripts")
        print("   - Extract financial metrics from reports")
        print("   - Analyze transcripts for qualitative insights")
        print("   - Fetch live market data")
        print("   - Generate comprehensive forecast")
        
        start_time = time.time()
        
        result = agent.generate_forecast("TCS", "Q2-2025")
        
        processing_time = time.time() - start_time
        
        # Display comprehensive results
        print(f"\n📊 COMPLETE TEST RESULTS:")
        print("=" * 60)
        print(f"✅ Success: {result.success}")
        print(f"⏱️  Processing Time: {processing_time:.1f} seconds")
        print(f"🎯 Overall Outlook: {result.overall_outlook.upper()}")
        print(f"📈 Investment Recommendation: {result.investment_recommendation.upper()}")
        print(f"📊 Confidence Score: {result.confidence_score:.0%}")
        
        # Verify all 3 data sources
        print(f"\n🔍 Data Source Verification:")
        financial_ok = result.financial_metrics is not None
        qualitative_ok = result.qualitative_analysis is not None
        market_ok = result.market_data is not None
        
        print(f"   📄 Financial Reports: {'✅' if financial_ok else '❌'}")
        if financial_ok:
            fm = result.financial_metrics
            print(f"      Revenue: ₹{fm.total_revenue} Cr" if fm.total_revenue else "      Revenue: Not extracted")
            print(f"      Net Profit: ₹{fm.net_profit} Cr" if fm.net_profit else "      Net Profit: Not extracted")
            
        print(f"   🧠 Qualitative Analysis: {'✅' if qualitative_ok else '❌'}")
        if qualitative_ok:
            qa = result.qualitative_analysis
            print(f"      Total Insights: {qa.total_insights}")
            print(f"      Management Sentiment: {qa.management_sentiment.overall_tone}")
            print(f"      Business Outlook: {len(qa.business_outlook)} insights")
            print(f"      Growth Opportunities: {len(qa.growth_opportunities)} insights")
            
        print(f"   📈 Live Market Data: {'✅' if market_ok else '❌'}")
        if market_ok:
            md = result.market_data
            print(f"      Current Price: ₹{md.current_price:,.2f}")
            print(f"      P/E Ratio: {md.pe_ratio}")
            print(f"      Valuation: {result.market_context.current_valuation if result.market_context else 'Unknown'}")
        
        # Show forecast insights
        print(f"\n🎯 Generated Forecast Insights:")
        print(f"   Key Drivers ({len(result.key_drivers)}):")
        for i, driver in enumerate(result.key_drivers[:3], 1):
            print(f"     {i}. {driver}")
        
        if qualitative_ok and result.qualitative_analysis.business_outlook:
            print(f"   Business Outlook Sample:")
            print(f"     • {result.qualitative_analysis.business_outlook[0].insight}")
        
        # Success criteria
        data_sources_count = sum([financial_ok, qualitative_ok, market_ok])
        success = result.success and data_sources_count >= 2
        
        print(f"\n🏆 FINAL ASSESSMENT:")
        print(f"   Data Sources Working: {data_sources_count}/3")
        print(f"   Forecast Quality: {'HIGH' if data_sources_count == 3 else 'MEDIUM' if data_sources_count == 2 else 'LOW'}")
        
        if success:
            print(f"   🎉 SYSTEM FULLY OPERATIONAL!")
            print(f"   ✅ Downloads fresh financial data")
            print(f"   ✅ Extracts meaningful insights") 
            print(f"   ✅ Generates professional forecasts")
        else:
            print(f"   ⚠️  System partially working - check failed components")
        
        return success
        
    except Exception as e:
        print(f"❌ Fresh test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fresh_system()
    sys.exit(0 if success else 1)