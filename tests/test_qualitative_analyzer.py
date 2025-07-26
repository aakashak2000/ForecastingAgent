#!/usr/bin/env python3

import logging
import sys
import os
import json
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_qualitative_analyzer():
    """Test the complete QualitativeAnalysisTool with real TCS transcript data"""
    
    print("🧪 Testing QualitativeAnalysisTool with TCS Earnings Data")
    print("=" * 70)
    
    try:
        from tools.qualitative_analyzer import QualitativeAnalysisTool
        
        # Check if vector store has data
        vector_store_path = Path("test_vectorstore_data") 
        if not vector_store_path.exists():
            print("❌ No vector store found")
            print("   Run test_vectorstore.py first to create vector store with transcript data")
            return False
        
        print(f"📊 Using vector store: {vector_store_path}")
        
        # Initialize qualitative analyzer
        print(f"\n🔧 Initializing QualitativeAnalysisTool...")
        analyzer = QualitativeAnalysisTool(vectorstore_dir="../data/vector_store")
        print("✅ QualitativeAnalysisTool initialized")
        
        # Run complete qualitative analysis
        print(f"\n🚀 Starting qualitative analysis...")
        print("   This will:")
        print("   1. Search vector store for relevant transcript chunks")
        print("   2. Analyze management sentiment with LLM")
        print("   3. Extract business outlook insights")
        print("   4. Identify risk factors and challenges") 
        print("   5. Find growth opportunities")
        print("   6. Structure all insights into comprehensive report")
        
        result = analyzer.analyze_transcripts(
            company_symbol="TCS",
            analysis_period="Q1-2025"
        )
        
        # Display results
        print(f"\n📊 Analysis Results:")
        print(f"   Success: {'✅' if result.success else '❌'}")
        print(f"   Processing Time: {result.processing_time:.2f} seconds")
        print(f"   Total Insights: {result.total_insights}")
        print(f"   Average Confidence: {result.average_confidence:.2f}")
        
        if not result.success:
            print(f"   Error: {result.error_message}")
            return False
        
        # Display management sentiment
        print(f"\n😊 Management Sentiment Analysis:")
        sentiment = result.management_sentiment
        print(f"   Overall Tone: {sentiment.overall_tone}")
        print(f"   Optimism Score: {sentiment.optimism_score:.2f}/1.0")
        print(f"   Key Themes: {', '.join(sentiment.key_themes[:3])}")
        
        if sentiment.forward_looking_statements:
            print(f"   Forward-Looking Statements:")
            for i, statement in enumerate(sentiment.forward_looking_statements[:2], 1):
                print(f"     {i}. {statement}")
        
        # Display business outlook insights
        print(f"\n🔮 Business Outlook ({len(result.business_outlook)} insights):")
        for i, insight in enumerate(result.business_outlook[:3], 1):
            print(f"   Insight #{i} (Confidence: {insight.confidence:.2f}):")
            print(f"     {insight.insight}")
            if insight.supporting_quotes and insight.supporting_quotes[0]:
                quote = insight.supporting_quotes[0][:100] + "..." if len(insight.supporting_quotes[0]) > 100 else insight.supporting_quotes[0]
                print(f"     Supporting Quote: \"{quote}\"")
            print()
        
        # Display risk factors
        print(f"⚠️  Risk Factors ({len(result.risk_factors)} insights):")
        for i, risk in enumerate(result.risk_factors[:2], 1):
            print(f"   Risk #{i} (Confidence: {risk.confidence:.2f}):")
            print(f"     {risk.insight}")
            if risk.supporting_quotes and risk.supporting_quotes[0]:
                quote = risk.supporting_quotes[0][:100] + "..." if len(risk.supporting_quotes[0]) > 100 else risk.supporting_quotes[0]
                print(f"     Supporting Quote: \"{quote}\"")
            print()
        
        # Display growth opportunities
        print(f"🚀 Growth Opportunities ({len(result.growth_opportunities)} insights):")
        for i, opportunity in enumerate(result.growth_opportunities[:2], 1):
            print(f"   Opportunity #{i} (Confidence: {opportunity.confidence:.2f}):")
            print(f"     {opportunity.insight}")
            if opportunity.supporting_quotes and opportunity.supporting_quotes[0]:
                quote = opportunity.supporting_quotes[0][:100] + "..." if len(opportunity.supporting_quotes[0]) > 100 else opportunity.supporting_quotes[0]
                print(f"     Supporting Quote: \"{quote}\"")
            print()
        
        # Show high-confidence insights summary
        high_conf_insights = result.get_high_confidence_insights(min_confidence=0.7)
        print(f"🎯 High-Confidence Insights (≥0.7): {len(high_conf_insights)}")
        
        for insight in high_conf_insights[:3]:
            print(f"   • [{insight.category.upper()}] {insight.insight[:80]}...")
        
        # Save complete results
        output_file = "test_qualitative_analysis_results.json"
        
        # Convert to dict for JSON serialization
        results_dict = {
            "analysis_summary": result.get_summary_dict(),
            "management_sentiment": {
                "overall_tone": sentiment.overall_tone,
                "optimism_score": sentiment.optimism_score,
                "key_themes": sentiment.key_themes,
                "forward_looking_statements": sentiment.forward_looking_statements
            },
            "insights_by_category": {
                "business_outlook": [
                    {
                        "insight": insight.insight,
                        "confidence": insight.confidence,
                        "supporting_quotes": insight.supporting_quotes
                    } for insight in result.business_outlook
                ],
                "risk_factors": [
                    {
                        "insight": insight.insight,
                        "confidence": insight.confidence,
                        "supporting_quotes": insight.supporting_quotes
                    } for insight in result.risk_factors
                ],
                "growth_opportunities": [
                    {
                        "insight": insight.insight,
                        "confidence": insight.confidence,
                        "supporting_quotes": insight.supporting_quotes
                    } for insight in result.growth_opportunities
                ]
            },
            "metadata": {
                "company": result.company_symbol,
                "period": result.analysis_period,
                "processing_time": result.processing_time,
                "total_insights": result.total_insights,
                "average_confidence": result.average_confidence
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(results_dict, f, indent=2, default=str)
        
        print(f"\n💾 Complete analysis saved to: {output_file}")
        print(f"🎉 Qualitative Analysis Test Complete!")
        
        # Success criteria
        success = (result.success and 
                  result.total_insights > 0 and 
                  len(sentiment.key_themes) > 0)
        
        if success:
            print(f"✅ SUCCESS: Extracted {result.total_insights} structured insights from earnings call!")
        else:
            print(f"⚠️  PARTIAL: Analysis completed but with limited insights")
        
        return success
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure all dependencies are installed")
        return False
        
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_qualitative_analyzer()
    sys.exit(0 if success else 1)