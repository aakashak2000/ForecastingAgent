#!/usr/bin/env python3

import json
from pathlib import Path

def fix_transcript_data():
    """Fix the transcript data using the successfully extracted content"""
    
    # Read the full extracted content
    if Path("manual_transcript_extraction.txt").exists():
        with open("manual_transcript_extraction.txt", 'r') as f:
            full_content = f.read()
        
        print(f"📄 Read extracted content: {len(full_content)} characters")
        
        # Create proper test data with full content
        fixed_data = {
            "company": "TCS",
            "annual_reports": [],
            "transcripts": [{
                "date": "Jul 2025",
                "transcript_url": "https://www.bseindia.com/stockinfo/AnnPdfOpen.aspx?Pname=9cee0fdb-07a3-4dc6-af7a-40dce51e1348.pdf",
                "notes_url": None,
                "source": "concall",
                "content": full_content[:1000] + "...",  # Preview
                "full_content": full_content,              # Complete content
                "word_count": len(full_content.split())
            }],
            "errors": []
        }
        
        # Save fixed data
        with open("test_downloader_results.json", 'w') as f:
            json.dump(fixed_data, f, indent=2)
        
        print(f"✅ Fixed transcript data:")
        print(f"   Content length: {len(full_content)} characters")
        print(f"   Word count: {len(full_content.split())}")
        print(f"   Saved to: test_downloader_results.json")
        
        return True
    else:
        print(f"❌ manual_transcript_extraction.txt not found")
        return False

if __name__ == "__main__":
    fix_transcript_data()
