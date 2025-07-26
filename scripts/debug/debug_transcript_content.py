#!/usr/bin/env python3

import json
from pathlib import Path

def debug_transcript_content():
    """Debug what's actually in our transcript data"""
    
    print("🔍 Debugging Transcript Content")
    print("=" * 50)
    
    # Load transcript data
    if Path("test_downloader_results.json").exists():
        with open("test_downloader_results.json", 'r') as f:
            data = json.load(f)
        
        transcripts = data.get('transcripts', [])
        if transcripts:
            transcript = transcripts[0]
            
            print(f"📝 Transcript Info:")
            print(f"   Date: {transcript['date']}")
            print(f"   Word Count: {transcript['word_count']}")
            
            # FIXED: Look for full_content first, then content
            full_content = transcript.get('full_content', transcript.get('content', ''))
            preview_content = transcript.get('content', '')
            
            print(f"\n📄 Content Analysis:")
            print(f"   Preview Content Length: {len(preview_content)} characters")
            print(f"   Full Content Length: {len(full_content)} characters")
            
            if len(full_content) > len(preview_content):
                print(f"   ✅ Found full content! Using {len(full_content)} characters")
                content_to_analyze = full_content
            else:
                print(f"   ⚠️  Only preview content available")
                content_to_analyze = preview_content
            
            print(f"\n   First 500 characters:")
            print(f"   {content_to_analyze[:500]}")
            
            if len(content_to_analyze) > 2500:
                print(f"\n   Middle section (chars 2000-2500):")
                print(f"   {content_to_analyze[2000:2500]}")
                print(f"\n   Last 500 characters:")
                print(f"   {content_to_analyze[-500:]}")
            
            # Check for earnings call content
            earnings_keywords = [
                'revenue', 'profit', 'growth', 'outlook', 'guidance', 
                'quarter', 'margin', 'performance', 'business', 'clients',
                'ceo', 'cfo', 'management', 'analyst', 'question', 'answer',
                'operator', 'good morning', 'thank you', 'conference call'
            ]
            
            print(f"\n🔍 Keyword Analysis:")
            keyword_counts = {}
            content_lower = content_to_analyze.lower()
            
            for keyword in earnings_keywords:
                count = content_lower.count(keyword)
                if count > 0:
                    keyword_counts[keyword] = count
            
            print(f"   Keywords found: {keyword_counts}")
            
            # Check if this is actually earnings call content
            transcript_indicators = sum(1 for word in ['earnings', 'conference', 'call', 'transcript', 
                                                      'ceo', 'cfo', 'analyst', 'operator'] 
                                      if word in content_lower)
            
            if transcript_indicators >= 3:
                print(f"   ✅ Strong indicators of actual earnings call transcript")
            elif len(keyword_counts) >= 3:
                print(f"   ✅ Contains earnings call content") 
            else:
                print(f"   ⚠️  May be administrative document, not actual transcript")
                
            return content_to_analyze
    
    return None

if __name__ == "__main__":
    debug_transcript_content()