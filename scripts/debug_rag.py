#!/usr/bin/env python3
"""
Debug RAG implementation - verify retrieval quality
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

def test_rag_pipeline():
    """Test the complete RAG pipeline"""
    print("🔍 DEBUGGING RAG IMPLEMENTATION")
    print("=" * 50)
    
    try:
        from vector_store.transcript_vectorstore import TranscriptVectorStore
        from tools.qualitative_analyzer import QualitativeAnalysisTool
        
        # Check vector store content
        print("\n📊 Vector Store Analysis:")
        vs = TranscriptVectorStore()
        stats = vs.get_collection_stats()
        print(f"   Total chunks: {stats.get('total_chunks', 0)}")
        print(f"   Companies: {stats.get('companies', [])}")
        print(f"   Chunk types: {stats.get('chunk_types', {})}")
        
        if stats.get('total_chunks', 0) == 0:
            print("   ❌ NO DATA IN VECTOR STORE!")
            return False
        
        # Test retrieval quality
        print(f"\n🔍 Testing Retrieval Quality:")
        
        test_queries = [
            "revenue growth outlook",
            "management guidance future",
            "cost optimization",
            "AI technology innovation",
            "business performance"
        ]
        
        for query in test_queries:
            results = vs.search_transcripts(query, "TCS", n_results=3, min_similarity=-1.0)
            print(f"\n   Query: '{query}'")
            print(f"   Results: {len(results)}")
            
            if results:
                best_result = results[0]
                similarity = best_result.get('similarity', 0)
                print(f"   Best similarity: {similarity:.3f}")
                if similarity > 0.3:  # Good similarity
                    print(f"   ✅ GOOD retrieval")
                elif similarity > 0.0:  # Okay similarity  
                    print(f"   ⚠️  FAIR retrieval")
                else:  # Poor similarity
                    print(f"   ❌ POOR retrieval")
                    
                print(f"   Sample text: {best_result['text'][:150]}...")
            else:
                print(f"   ❌ NO RESULTS")
        
        # Test end-to-end RAG
        print(f"\n🧠 Testing End-to-End RAG:")
        analyzer = QualitativeAnalysisTool()
        result = analyzer.analyze_transcripts("TCS", "Q1-2025")
        
        print(f"   Analysis success: {result.success}")
        print(f"   Total insights: {result.total_insights}")
        print(f"   Avg confidence: {result.average_confidence:.2f}")
        
        if result.business_outlook:
            print(f"   Sample insight: {result.business_outlook[0].insight}")
            print(f"   Supporting quote: {result.business_outlook[0].supporting_quotes[0] if result.business_outlook[0].supporting_quotes else 'None'}")
        
        # Conclusion
        if result.total_insights > 0 and result.average_confidence > 0.5:
            print(f"\n✅ RAG IS WORKING EFFECTIVELY")
            return True
        else:
            print(f"\n❌ RAG IS NOT WORKING WELL")
            return False
            
    except Exception as e:
        print(f"❌ RAG test failed: {e}")
        return False

if __name__ == "__main__":
    test_rag_pipeline()