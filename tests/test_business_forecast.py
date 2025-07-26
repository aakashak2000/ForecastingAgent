#!/usr/bin/env python3
"""
Business-oriented forecast test - generates comprehensive, professional output
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

def generate_business_forecast():
    """Generate comprehensive business-grade forecast"""
    
    print("💼 FINANCIAL FORECASTING AGENT - BUSINESS REPORT")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print(f"Report Type: Quarterly Business Outlook Forecast")
    
    try:
        from agent.orchestrator import FinancialForecastingAgent
        
        # Initialize agent
        agent = FinancialForecastingAgent()
        
        # Generate comprehensive forecast
        print(f"\n🔄 Analyzing TCS Financial Position...")
        result = agent.generate_forecast("TCS", "Q2-2025")
        
        if not result.success:
            print(f"❌ Forecast generation failed: {result.error_message}")
            return False
        
        # Create business-grade report
        create_business_report(result)
        
        # Save structured output for business systems
        save_business_json(result)
        
        return True
        
    except Exception as e:
        print(f"❌ Business forecast failed: {e}")
        return False

def create_business_report(result):
    """Create comprehensive business report"""
    
    print(f"\n📊 EXECUTIVE SUMMARY")
    print("─" * 50)
    print(f"Company: Tata Consultancy Services (TCS)")
    print(f"Forecast Period: {result.forecast_period}")
    print(f"Investment Thesis: {result.overall_outlook.upper()} outlook")
    print(f"Recommendation: {result.investment_recommendation.upper()}")
    print(f"Analyst Confidence: {result.confidence_score:.0%}")
    
    # Financial Metrics Section
    print(f"\n💰 FINANCIAL ANALYSIS")
    print("─" * 50)
    
    if result.market_data:
        market_cap_cr = result.market_data.market_cap
        print(f"Current Stock Price: ₹{result.market_data.current_price:,.2f}")
        print(f"Market Capitalization: ₹{market_cap_cr:,.0f} Crores (${market_cap_cr*0.12:.1f}B USD)")
        print(f"Price Performance: {result.market_data.price_change_percent:+.1f}% (₹{result.market_data.price_change:+.2f})")
        print(f"Trading Volume: {result.market_data.volume:,} shares")
        print(f"P/E Ratio: {result.market_data.pe_ratio:.1f}x")
        print(f"52-Week Range: ₹{result.market_data.week_52_low:,.0f} - ₹{result.market_data.week_52_high:,.0f}")
        
        # Calculate position in range
        range_position = ((result.market_data.current_price - result.market_data.week_52_low) / 
                         (result.market_data.week_52_high - result.market_data.week_52_low)) * 100
        print(f"Range Position: {range_position:.0f}% of 52-week range")
    
    # Add historical context if available
    if hasattr(result, 'financial_metrics') and result.financial_metrics:
        print(f"\nHistorical Metrics (Latest Available):")
        fm = result.financial_metrics
        if fm.total_revenue:
            print(f"Revenue: ₹{fm.total_revenue:,.0f} Crores")
        if fm.net_profit:
            print(f"Net Profit: ₹{fm.net_profit:,.0f} Crores")
        if fm.operating_margin:
            print(f"Operating Margin: {fm.operating_margin:.1f}%")
    
    # Market Context
    print(f"\n📈 MARKET CONTEXT")
    print("─" * 50)
    
    if result.market_context:
        mc = result.market_context
        print(f"Valuation Assessment: {mc.current_valuation.replace('_', ' ').title()}")
        print(f"Price Momentum: {mc.price_momentum.title()}")
        print(f"Risk Level: {mc.risk_level.title()}")
        
        print(f"\nMarket Position Analysis:")
        for observation in mc.key_observations:
            print(f"  • {observation}")
    
    # Management Insights
    print(f"\n🎯 MANAGEMENT INSIGHTS")
    print("─" * 50)
    
    if result.qualitative_analysis:
        qa = result.qualitative_analysis
        sentiment = qa.management_sentiment
        
        print(f"Management Sentiment: {sentiment.overall_tone.title()} (Optimism: {sentiment.optimism_score:.0%})")
        
        if sentiment.key_themes:
            print(f"\nKey Management Themes:")
            for theme in sentiment.key_themes[:4]:
                print(f"  • {theme}")
        
        # Business outlook insights
        if qa.business_outlook:
            print(f"\nBusiness Outlook ({len(qa.business_outlook)} insights):")
            for insight in qa.business_outlook:
                confidence_indicator = "🔹" if insight.confidence > 0.7 else "🔸"
                print(f"  {confidence_indicator} {insight.insight}")
        
        # Growth opportunities
        if qa.growth_opportunities:
            print(f"\nGrowth Opportunities:")
            for opportunity in qa.growth_opportunities:
                print(f"  🚀 {opportunity.insight}")
        
        # Risk factors
        if qa.risk_factors:
            print(f"\nRisk Factors:")
            for risk in qa.risk_factors:
                print(f"  ⚠️  {risk.insight}")
    
    # Investment Analysis
    print(f"\n🎯 INVESTMENT ANALYSIS")
    print("─" * 50)
    
    print(f"Primary Forecast Drivers:")
    for i, driver in enumerate(result.key_drivers, 1):
        print(f"  {i}. {driver.title()}")
    
    # Generate specific recommendations based on data
    print(f"\nInvestment Rationale:")
    if result.investment_recommendation.lower() == "buy":
        print(f"  • Strong fundamentals support accumulation at current levels")
        if result.market_data and result.market_data.price_change_percent > 0:
            print(f"  • Positive momentum with {result.market_data.price_change_percent:+.1f}% daily gain")
        print(f"  • Management optimism and strategic initiatives create upside potential")
        
        # Price targets (indicative)
        if result.market_data:
            current_price = result.market_data.current_price
            target_price = current_price * 1.15  # 15% upside assumption
            print(f"  • 12-month target price: ₹{target_price:,.0f} (+{((target_price/current_price)-1)*100:.0f}% upside)")
    
    elif result.investment_recommendation.lower() == "hold":
        print(f"  • Balanced risk-reward profile at current valuation")
        print(f"  • Await clearer fundamental catalysts for position sizing")
    
    # Risk assessment
    print(f"\nKey Risks to Monitor:")
    if result.market_context and result.market_context.risk_level == "high":
        print(f"  • High market risk due to current price positioning")
    print(f"  • Sector-specific headwinds from economic uncertainty")
    print(f"  • Execution risk on strategic transformation initiatives")
    
    # Processing metadata
    print(f"\n📋 ANALYSIS METADATA")
    print("─" * 50)
    print(f"Processing Time: {result.processing_time:.1f} seconds")
    print(f"Data Sources: Market data, earnings transcripts, financial reports")
    print(f"Analysis Confidence: {result.confidence_score:.0%}")
    
    print(f"\n" + "="*70)
    print(f"This analysis combines quantitative financial metrics, qualitative")
    print(f"management insights, and real-time market data for comprehensive")
    print(f"investment decision support.")

def save_business_json(result):
    """Save machine-readable business data"""
    
    # Create comprehensive business JSON
    business_data = {
        "report_metadata": {
            "company": result.company_symbol,
            "forecast_period": result.forecast_period,
            "generated_at": datetime.now().isoformat(),
            "processing_time_seconds": result.processing_time,
            "analyst_confidence": result.confidence_score
        },
        "investment_summary": {
            "recommendation": result.investment_recommendation,
            "outlook": result.overall_outlook,
            "confidence_score": result.confidence_score,
            "key_drivers": result.key_drivers
        },
        "market_data": {
            "current_price": result.market_data.current_price if result.market_data else None,
            "price_change_percent": result.market_data.price_change_percent if result.market_data else None,
            "market_cap_crores": result.market_data.market_cap if result.market_data else None,
            "pe_ratio": result.market_data.pe_ratio if result.market_data else None,
            "week_52_high": result.market_data.week_52_high if result.market_data else None,
            "week_52_low": result.market_data.week_52_low if result.market_data else None
        },
        "market_context": {
            "valuation": result.market_context.current_valuation if result.market_context else None,
            "momentum": result.market_context.price_momentum if result.market_context else None,
            "risk_level": result.market_context.risk_level if result.market_context else None
        },
        "qualitative_analysis": {
            "management_sentiment": result.qualitative_analysis.management_sentiment.overall_tone if result.qualitative_analysis else None,
            "optimism_score": result.qualitative_analysis.management_sentiment.optimism_score if result.qualitative_analysis else None,
            "total_insights": result.qualitative_analysis.total_insights if result.qualitative_analysis else 0,
            "business_outlook_count": len(result.qualitative_analysis.business_outlook) if result.qualitative_analysis else 0,
            "growth_opportunities_count": len(result.qualitative_analysis.growth_opportunities) if result.qualitative_analysis else 0,
            "risk_factors_count": len(result.qualitative_analysis.risk_factors) if result.qualitative_analysis else 0
        }
    }
    
    # Save to file
    output_file = "business_forecast_output.json"
    with open(output_file, 'w') as f:
        json.dump(business_data, f, indent=2, default=str)
    
    print(f"\n💾 Business data saved to: {output_file}")
    print(f"   Use this JSON for business system integration")

if __name__ == "__main__":
    success = generate_business_forecast()
    sys.exit(0 if success else 1)