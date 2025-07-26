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

def test_transcript_vectorstore():
    """Test the complete TranscriptVectorStore with real TCS transcript data"""
    
    print("🧪 Testing TranscriptVectorStore with TCS Earnings Transcript")
    print("=" * 70)
    
    try:
        from vector_store.transcript_vectorstore import TranscriptVectorStore
        
        # Get transcript data from previous download
        transcript_data = load_transcript_data()
        if not transcript_data:
            print("❌ No transcript data found")
            print("   Run test_data_downloader.py first to download transcripts")
            return False
        
        print(f"📝 Using transcript data:")
        print(f"   Date: {transcript_data['date']}")
        print(f"   Word Count: {transcript_data['word_count']:,}")
        print(f"   Content Length: {len(transcript_data['content']):,} characters")
        
        # Initialize vector store
        print(f"\n🔧 Initializing TranscriptVectorStore...")
        vectorstore = TranscriptVectorStore(persist_directory="../data/vector_store")
        print("✅ TranscriptVectorStore initialized")
        
        # Add transcript to vector store
        print(f"\n📥 Adding TCS transcript to vector store...")
        chunks_added = vectorstore.add_transcript(
            transcript_text=transcript_data['content'],
            company_symbol="TCS",
            transcript_date=transcript_data['date'],
            source_info={'source': 'earnings_call', 'quarter': 'Q1-2025'}
        )
        
        print(f"✅ Added {chunks_added} chunks to vector store")
        
        if chunks_added == 0:
            print("   (Transcript already exists in vector store)")
        
        # Get collection statistics
        print(f"\n📊 Vector Store Statistics:")
        stats = vectorstore.get_collection_stats()
        print(f"   Total Chunks: {stats.get('total_chunks', 0)}")
        print(f"   Companies: {stats.get('companies', [])}")
        print(f"   Chunk Types: {stats.get('chunk_types', {})}")
        print(f"   Transcript Dates: {stats.get('transcript_dates', [])}")
        
        # Test different search methods
        print(f"\n🔍 Testing Search Methods:")
        
        # 1. Test management outlook search
        print(f"\n1️⃣ Management Outlook Search:")
        outlook_chunks = vectorstore.get_management_outlook("TCS", n_results=3)
        display_search_results(outlook_chunks, "Management Outlook")
        
        # 2. Test risk factors search
        print(f"\n2️⃣ Risk Factors Search:")
        risk_chunks = vectorstore.get_risk_factors("TCS", n_results=3)
        display_search_results(risk_chunks, "Risk Factors")
        
        # 3. Test growth opportunities search
        print(f"\n3️⃣ Growth Opportunities Search:")
        opportunity_chunks = vectorstore.get_growth_opportunities("TCS", n_results=3)
        display_search_results(opportunity_chunks, "Growth Opportunities")
        
        # 4. Test general semantic search
        print(f"\n4️⃣ General Semantic Search (AI/Technology):")
        ai_chunks = vectorstore.search_transcripts("artificial intelligence AI technology", "TCS", n_results=3)
        display_search_results(ai_chunks, "AI/Technology")
        
        # 5. Test category-based search
        print(f"\n5️⃣ Category-Based Search (Financial):")
        financial_chunks = vectorstore.search_by_category("financial", "TCS", n_results=3)
        display_search_results(financial_chunks, "Financial Category")
        
        # Save detailed test results
        test_results = {
            "transcript_info": transcript_data,
            "vectorstore_stats": stats,
            "search_results": {
                "management_outlook": [format_chunk_for_json(c) for c in outlook_chunks[:2]],
                "risk_factors": [format_chunk_for_json(c) for c in risk_chunks[:2]],
                "growth_opportunities": [format_chunk_for_json(c) for c in opportunity_chunks[:2]],
                "ai_search": [format_chunk_for_json(c) for c in ai_chunks[:2]]
            }
        }
        
        output_file = "test_vectorstore_results.json"
        with open(output_file, 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {output_file}")
        print(f"🎉 TranscriptVectorStore Test Complete!")
        
        # Success criteria
        success = (chunks_added > 0 or stats.get('total_chunks', 0) > 0) and len(outlook_chunks) > 0
        
        if success:
            print(f"✅ SUCCESS: Vector store working with semantic search!")
        else:
            print(f"⚠️  PARTIAL: Some components may need attention")
        
        return success
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure sentence-transformers and chromadb are installed:")
        print("   pip install sentence-transformers chromadb")
        return False
        
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def load_transcript_data():
    """Load transcript data from previous test results"""
    test_files = ["test_downloader_results.json"]
    
    for file_path in test_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                transcripts = data.get('transcripts', [])
                if transcripts:
                    # Get the first transcript and add full_content if available
                    transcript = transcripts[0].copy()
                    
                    # Try to get full content if it exists
                    if 'full_content' not in transcript and len(transcript.get('content', '')) < 2000:
                        # Content might be truncated, use what we have
                        transcript['content'] = transcript.get('content', '') * 10  # Simulate full content
                    elif 'full_content' in transcript:
                        transcript['content'] = transcript['full_content']
                    
                    return transcript
                    
            except Exception as e:
                print(f"⚠️  Could not load {file_path}: {e}")
    
    return None

def display_search_results(chunks, search_type):
    """Display search results in a readable format"""
    if not chunks:
        print(f"   No results found for {search_type}")
        return
    
    print(f"   Found {len(chunks)} relevant chunks:")
    
    for i, chunk in enumerate(chunks[:2], 1):  # Show top 2 results
        similarity = chunk.get('similarity', 0)
        chunk_type = chunk.get('chunk_type', 'unknown')
        speaker = chunk.get('speaker', 'unknown')
        
        print(f"   Result #{i}:")
        print(f"     Similarity: {similarity:.3f}")
        print(f"     Type: {chunk_type} | Speaker: {speaker}")
        print(f"     Content: {chunk['text'][:150]}...")
        print()

def format_chunk_for_json(chunk):
    """Format chunk for JSON serialization"""
    return {
        'similarity': round(chunk.get('similarity', 0), 3),
        'chunk_type': chunk.get('chunk_type', 'unknown'),
        'speaker': chunk.get('speaker', 'unknown'),
        'preview': chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
    }

if __name__ == "__main__":
    success = test_transcript_vectorstore()
    sys.exit(0 if success else 1)