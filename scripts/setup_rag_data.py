#!/usr/bin/env python3
"""
Setup RAG data - Download and populate vector store with transcript data
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

def setup_rag_data():
    """Download transcripts and populate vector store"""
    print("🔄 SETTING UP RAG DATA - DOWNLOADING TRANSCRIPTS")
    print("=" * 60)
    
    try:
        from utils.data_downloader import ScreenerDataDownloader
        from vector_store.transcript_vectorstore import TranscriptVectorStore
        
        # Step 1: Download transcript data
        print("📥 Step 1: Downloading TCS transcript data...")
        downloader = ScreenerDataDownloader()
        
        # Get latest documents
        results = downloader.get_latest_documents("TCS", max_reports=0, max_transcripts=3)
        
        if not results['transcripts']:
            print("❌ No transcripts downloaded")
            return False
        
        print(f"✅ Downloaded {len(results['transcripts'])} transcripts")
        for t in results['transcripts']:
            print(f"   - {t['date']}: {t['word_count']} words")
        
        # Step 2: Initialize vector store
        print(f"\n🧠 Step 2: Setting up vector store...")
        vectorstore = TranscriptVectorStore(persist_directory="data/vector_store")
        
        # Step 3: Add transcripts to vector store
        print(f"\n📝 Step 3: Adding transcripts to vector store...")
        total_chunks = 0
        
        for transcript in results['transcripts']:
            content = transcript.get('full_content', transcript.get('content', ''))
            if len(content) < 5000:
                print(f"   ⚠️  Skipping short transcript: {transcript['date']}")
                continue
                
            chunks_added = vectorstore.add_transcript(
                transcript_text=content,
                company_symbol="TCS",
                transcript_date=transcript['date'],
                source_info={
                    'source': 'earnings_call',
                    'quarter': 'Q1-2025',
                    'word_count': transcript['word_count']
                }
            )
            
            total_chunks += chunks_added
            print(f"   ✅ {transcript['date']}: {chunks_added} chunks")
        
        print(f"\n📊 RAG Data Setup Complete!")
        print(f"   Total chunks added: {total_chunks}")
        
        # Step 4: Test retrieval
        print(f"\n🔍 Step 4: Testing RAG retrieval...")
        
        test_queries = [
            "revenue growth outlook",
            "management guidance",
            "cost optimization",
            "business performance"
        ]
        
        for query in test_queries:
            results = vectorstore.search_transcripts(query, "TCS", n_results=2)
            if results:
                best_similarity = max(r.get('similarity', 0) for r in results)
                print(f"   Query '{query}': {len(results)} results, best similarity: {best_similarity:.3f}")
            else:
                print(f"   Query '{query}': No results")
        
        # Step 5: Get final stats
        stats = vectorstore.get_collection_stats()
        print(f"\n✅ RAG SETUP SUCCESSFUL!")
        print(f"   Vector store now contains: {stats.get('total_chunks', 0)} chunks")
        print(f"   Companies: {stats.get('companies', [])}")
        print(f"   Ready for qualitative analysis!")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_rag_data()
    if success:
        print(f"\nSuccess!")
    sys.exit(0 if success else 1)
