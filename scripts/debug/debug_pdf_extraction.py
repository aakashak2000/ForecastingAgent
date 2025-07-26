#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_downloader import ScreenerDataDownloader

def debug_pdf_extraction():
    """Debug the PDF extraction method directly"""
    
    print("🔍 Debugging PDF Extraction Method")
    print("=" * 50)
    
    downloader = ScreenerDataDownloader()
    
    # Test transcript URL (the same one that worked before)
    transcript_url = "https://www.bseindia.com/stockinfo/AnnPdfOpen.aspx?Pname=9cee0fdb-07a3-4dc6-af7a-40dce51e1348.pdf"
    
    print(f"📄 Testing direct PDF extraction from:")
    print(f"   {transcript_url[:80]}...")
    
    # Call the extraction method directly
    extracted_content = downloader.extract_transcript_content(transcript_url)
    
    if extracted_content:
        print(f"\n✅ Extraction Results:")
        print(f"   Content Length: {len(extracted_content)} characters")
        print(f"   Word Count: {len(extracted_content.split())}")
        
        print(f"\n📝 Content Preview:")
        print(f"   First 500 chars: {extracted_content[:500]}")
        
        if len(extracted_content) > 2000:
            print(f"\n   Middle section: {extracted_content[1000:1500]}")
            print(f"\n   Last 500 chars: {extracted_content[-500:]}")
        
        # Check for actual transcript content
        transcript_keywords = ['ceo', 'cfo', 'analyst', 'operator', 'question', 'answer', 'revenue', 'profit']
        content_lower = extracted_content.lower()
        found_keywords = [kw for kw in transcript_keywords if kw in content_lower]
        
        print(f"\n🔍 Transcript Keywords Found: {found_keywords}")
        
        if len(found_keywords) >= 3:
            print(f"✅ This appears to be actual earnings call content!")
        else:
            print(f"⚠️  This may be just administrative content")
            
        return extracted_content
    else:
        print(f"❌ Extraction failed or returned None")
        return None

if __name__ == "__main__":
    content = debug_pdf_extraction()
    
    if content and len(content) > 10000:
        # Save the good content for manual inspection
        with open("manual_transcript_extraction.txt", 'w') as f:
            f.write(content)
        print(f"\n💾 Full content saved to: manual_transcript_extraction.txt")