#!/usr/bin/env python3

import logging
import sys
import os
import json
import glob
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_financial_extractor():
    """Test the complete FinancialDataExtractorTool with real TCS data"""
    
    print("🧪 Testing FinancialDataExtractorTool with TCS Annual Report")
    print("=" * 70)
    
    try:
        from tools.financial_extractor import FinancialDataExtractorTool
        
        # Find the TCS PDF
        search_patterns = [
            "temp_downloads/*TCS*.pdf",
            "/var/folders/*/T/*TCS*.pdf",
            "/tmp/*TCS*.pdf"
        ]
        
        pdf_path = None
        for pattern in search_patterns:
            files = glob.glob(pattern)
            if files:
                pdf_path = files[0]
                break
        
        if not pdf_path:
            print("❌ No TCS PDF found")
            print("   Run test_data_downloader.py first to download PDF")
            return False
        
        print(f"📄 Using PDF: {Path(pdf_path).name}")
        print(f"   Full path: {pdf_path}")
        print(f"   File size: {os.path.getsize(pdf_path)/1024:.1f} KB")
        
        # Initialize the financial extractor
        print(f"\n🔧 Initializing FinancialDataExtractorTool...")
        extractor = FinancialDataExtractorTool()
        print("✅ FinancialDataExtractorTool initialized")
        
        # Run the complete extraction process
        print(f"\n🚀 Starting financial data extraction...")
        print("   This will:")
        print("   1. Extract tables from PDF using pdfplumber")
        print("   2. Parse tables with LLM to get structured metrics") 
        print("   3. Validate and structure the financial data")
        
        result = extractor.extract_financial_data(
            pdf_path=pdf_path,
            company_symbol="TCS", 
            report_period="FY2025"
        )
        
        # Display results
        print(f"\n📊 Extraction Results:")
        print(f"   Success: {'✅' if result.success else '❌'}")
        print(f"   Processing Time: {result.processing_time:.2f} seconds")
        
        if not result.success:
            print(f"   Error: {result.error_message}")
            return False
        
        # Show extracted financial metrics
        metrics = result.metrics
        print(f"\n💰 Extracted Financial Metrics for {metrics.company_symbol} ({metrics.report_period}):")
        print(f"   Currency: {metrics.currency}")
        print(f"   Total Revenue: {metrics.total_revenue} Crores" if metrics.total_revenue else "   Total Revenue: Not found")
        print(f"   Net Profit: {metrics.net_profit} Crores" if metrics.net_profit else "   Net Profit: Not found")
        print(f"   Operating Profit: {metrics.operating_profit} Crores" if metrics.operating_profit else "   Operating Profit: Not found")
        print(f"   Operating Margin: {metrics.operating_margin}%" if metrics.operating_margin else "   Operating Margin: Not found")
        print(f"   Net Margin: {metrics.net_margin}%" if metrics.net_margin else "   Net Margin: Not found")
        print(f"   Extraction Confidence: {metrics.extraction_confidence:.2f}/1.0")
        
        # Show some raw source context if available
        if metrics.raw_source:
            print(f"\n📝 Raw Source Context (first 200 chars):")
            print(f"   {metrics.raw_source[:200]}...")
        
        # Save complete results
        output_file = "test_financial_extraction_results.json"
        
        # Convert to dict for JSON serialization
        results_dict = {
            "extraction_result": result.model_dump(),
            "financial_metrics": metrics.model_dump() if metrics else None,
            "source_pdf": pdf_path,
            "timestamp": str(result.processing_time)
        }
        
        with open(output_file, 'w') as f:
            json.dump(results_dict, f, indent=2, default=str)
        
        print(f"\n💾 Complete results saved to: {output_file}")
        print(f"🎉 Financial Data Extraction Test Complete!")
        
        # Success criteria
        success = (result.success and 
                  metrics and 
                  (metrics.total_revenue or metrics.net_profit))
        
        if success:
            print(f"✅ SUCCESS: Extracted meaningful financial data!")
        else:
            print(f"⚠️  PARTIAL: Extraction completed but with limited data")
        
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
    success = test_financial_extractor()
    sys.exit(0 if success else 1)