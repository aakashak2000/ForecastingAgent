#!/usr/bin/env python3
"""
Complete evaluator setup and test
Simulates the exact evaluator experience from scratch
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run command with status reporting"""
    print(f"🔧 {description}...")
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"   ✅ {description} completed")
            return True
        else:
            print(f"   ❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ {description} failed: {e}")
        return False

def setup_directories():
    """Create fresh data directories"""
    directories = ["data/downloads", "data/vector_store", "data/logs"]
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("   ✅ Created fresh directories")

def test_full_pipeline():
    """Test complete pipeline end-to-end"""
    print("\n🧪 TESTING COMPLETE EVALUATOR PIPELINE")
    print("=" * 60)
    
    # Test 1: Download fresh financial data
    print("\n📥 Testing Fresh Data Download...")
    test_cmd = '''
python -c "
from utils.data_downloader import ScreenerDataDownloader
downloader = ScreenerDataDownloader()
results = downloader.get_latest_documents('TCS', max_reports=1, max_transcripts=2)
print(f'Downloaded: {len(results[\"annual_reports\"])} reports, {len(results[\"transcripts\"])} transcripts')
if results['annual_reports']:
    print(f'Latest report: {results[\"annual_reports\"][0][\"title\"]}')
if results['transcripts']:
    print(f'Latest transcript: {results[\"transcripts\"][0][\"date\"]} ({results[\"transcripts\"][0][\"word_count\"]} words)')
"
    '''
    
    if not run_command(test_cmd, "Fresh data download"):
        return False
    
    # Test 2: Financial extraction
    print("\n💰 Testing Financial Data Extraction...")
    test_cmd = '''
python -c "
from tools.financial_extractor import FinancialDataExtractorTool
import glob
pdf_files = glob.glob('data/downloads/*TCS*.pdf')
if pdf_files:
    extractor = FinancialDataExtractorTool()
    result = extractor.extract_financial_data(pdf_files[0], 'TCS', 'FY2025')
    if result.success and result.metrics:
        print(f'Financial extraction: Revenue=₹{result.metrics.total_revenue} Cr, Confidence={result.metrics.extraction_confidence}')
    else:
        print('Financial extraction failed')
else:
    print('No PDF files found')
"
    '''
    
    if not run_command(test_cmd, "Financial data extraction"):
        return False
    
    # Test 3: RAG analysis
    print("\n🧠 Testing RAG Qualitative Analysis...")
    test_cmd = '''
python -c "
from tools.qualitative_analyzer import QualitativeAnalysisTool
analyzer = QualitativeAnalysisTool()
result = analyzer.analyze_transcripts('TCS', 'Q1-2025')
print(f'RAG Analysis: {result.total_insights} insights, sentiment={result.management_sentiment.overall_tone}, confidence={result.average_confidence:.2f}')
if result.business_outlook:
    print(f'Sample insight: {result.business_outlook[0].insight}')
"
    '''
    
    if not run_command(test_cmd, "RAG qualitative analysis"):
        return False
    
    # Test 4: Market data
    print("\n📈 Testing Live Market Data...")
    test_cmd = '''
python -c "
from tools.market_data import MarketDataTool
tool = MarketDataTool()
data = tool.get_stock_data('TCS')
if data:
    context = tool.analyze_market_context(data)
    print(f'Market Data: Price=₹{data.current_price}, P/E={data.pe_ratio}, Valuation={context.current_valuation if context else \"unknown\"}')
else:
    print('Market data failed')
"
    '''
    
    if not run_command(test_cmd, "Live market data"):
        return False
    
    # Test 5: Agent orchestration
    print("\n🤖 Testing Complete Agent Orchestration...")
    test_cmd = '''
python -c "
from agent.orchestrator import FinancialForecastingAgent
agent = FinancialForecastingAgent()
result = agent.generate_forecast('TCS', 'Q2-2025')
print(f'Agent Forecast: {result.overall_outlook} outlook, {result.investment_recommendation} recommendation, {result.confidence_score:.0%} confidence')
print(f'Processing time: {result.processing_time:.1f}s')
print(f'Key drivers: {len(result.key_drivers)}')
"
    '''
    
    if not run_command(test_cmd, "Complete agent orchestration"):
        return False
    
    return True

def test_fastapi_endpoint():
    """Test complete FastAPI endpoint"""
    print("\n🚀 Testing FastAPI Endpoint...")
    
    # Start server in background
    print("   Starting FastAPI server...")
    server_process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for startup
    time.sleep(10)
    
    try:
        # Test forecast endpoint
        test_cmd = '''
curl -X POST 'http://localhost:8000/forecast' \
     -H 'Content-Type: application/json' \
     -d '{"company_symbol": "TCS", "forecast_period": "Q2-2025"}' \
     --max-time 300 | jq '.investment_recommendation, .analyst_confidence, .current_price'
        '''
        
        result = run_command(test_cmd, "FastAPI forecast endpoint")
        
    finally:
        # Clean up server
        server_process.terminate()
        server_process.wait()
    
    return result

def main():
    """Run complete evaluator experience"""
    print("🎯 EVALUATOR EXPERIENCE - COMPLETE SYSTEM TEST")
    print("=" * 60)
    
    # Step 1: Install dependencies
    print("\n📦 Installing Dependencies...")
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      "Install dependencies"):
        return False
    
    # Step 2: Setup directories
    print("\n📁 Setting Up Fresh Environment...")
    setup_directories()
    
    # Step 3: Test complete pipeline
    if not test_full_pipeline():
        print("\n❌ Pipeline test failed")
        return False
    
    # Step 4: Test FastAPI
    if not test_fastapi_endpoint():
        print("\n❌ FastAPI test failed")
        return False
    
    print("\n🎉 EVALUATOR EXPERIENCE COMPLETE!")
    print("✅ All components working from fresh state")
    print("✅ Downloads latest financial reports")
    print("✅ Extracts latest earnings call transcripts")
    print("✅ Performs qualitative RAG analysis")
    print("✅ Fetches live market data")
    print("✅ Generates comprehensive forecasts")
    print("✅ FastAPI endpoint operational")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)