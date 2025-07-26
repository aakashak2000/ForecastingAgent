#!/usr/bin/env python3

import logging
import sys
import os
import json
from pprint import pprint

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_data_downloader():
    """Test the complete data downloader with real TCS data"""
    
    print("🧪 Testing Screener Data Downloader with TCS")
    print("=" * 60)
    
    try:
        from utils.data_downloader import ScreenerDataDownloader
        
        # Initialize downloader
        downloader = ScreenerDataDownloader()
        print("✅ ScreenerDataDownloader initialized")
        
        # Test document discovery first
        print("\n🔍 Step 1: Discovering available documents...")
        documents = downloader.get_company_documents("TCS")
        
        print(f"\n📋 Discovery Results:")
        print(f"   Annual Reports Found: {len(documents['annual_reports'])}")
        print(f"   Concalls Found: {len(documents['concalls'])}")
        
        # Show first few results
        if documents['annual_reports']:
            print(f"\n📄 Sample Annual Reports:")
            for i, report in enumerate(documents['annual_reports'][:3]):
                print(f"   {i+1}. {report['title']} ({report['year']})")
                print(f"      URL: {report['pdf_url'][:80]}...")
        
        if documents['concalls']:
            print(f"\n🎤 Sample Concalls:")
            for i, concall in enumerate(documents['concalls'][:3]):
                print(f"   {i+1}. {concall['date']}")
                print(f"      Transcript: {'✅' if concall['transcript_url'] else '❌'}")
                print(f"      Notes: {'✅' if concall['notes_url'] else '❌'}")
        
        # Test complete document retrieval
        print(f"\n📥 Step 2: Downloading latest documents...")
        results = downloader.get_latest_documents("TCS", max_reports=1, max_transcripts=1)
        
        print(f"\n🎯 Download Results:")
        print(f"   Annual Reports Downloaded: {len(results['annual_reports'])}")
        print(f"   Transcripts Extracted: {len(results['transcripts'])}")
        print(f"   Errors: {len(results['errors'])}")
        
        # Show detailed results
        if results['annual_reports']:
            report = results['annual_reports'][0]
            print(f"\n📊 Downloaded Annual Report:")
            print(f"   Title: {report['title']}")
            print(f"   Year: {report['year']}")
            print(f"   Local Path: {report['local_path']}")
            print(f"   File Size: {os.path.getsize(report['local_path'])/1024:.1f} KB")
        
        if results['transcripts']:
            transcript = results['transcripts'][0]
            print(f"\n📝 Extracted Transcript:")
            print(f"   Date: {transcript['date']}")
            print(f"   Word Count: {transcript['word_count']}")
            print(f"   Content Preview: {transcript['content'][:200]}...")
        
        if results['errors']:
            print(f"\n⚠️  Errors Encountered:")
            for error in results['errors']:
                print(f"   - {error}")
        
        # Save detailed results to file for inspection
        output_file = "test_downloader_results.json"
        with open(output_file, 'w') as f:
            # Remove full_content for cleaner JSON (it's very long)
            clean_results = results.copy()
            for transcript in clean_results.get('transcripts', []):
                transcript.pop('full_content', None)
            
            json.dump(clean_results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {output_file}")
        print(f"\n🎉 Data Downloader Test Complete!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure you've created utils/data_downloader.py")
        return False
        
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_temp_files():
    """Clean up any temporary PDF files created during testing"""
    import tempfile
    import glob
    
    temp_dir = tempfile.gettempdir()
    pdf_files = glob.glob(os.path.join(temp_dir, "*TCS*.pdf"))
    
    for file_path in pdf_files:
        try:
            os.remove(file_path)
            print(f"🧹 Cleaned up: {file_path}")
        except Exception as e:
            print(f"⚠️  Could not remove {file_path}: {e}")

if __name__ == "__main__":
    try:
        success = test_data_downloader()
        
        # Optional cleanup
        response = input("\n🧹 Clean up temporary PDF files? (y/n): ")
        if response.lower() == 'y':
            cleanup_temp_files()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)