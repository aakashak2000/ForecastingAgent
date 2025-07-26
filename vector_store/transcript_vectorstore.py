import logging
import hashlib
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class TranscriptVectorStore:
    """
    Manages vector storage and semantic search for earnings call transcripts
    """
    
    def __init__(self, persist_directory: str = "vector_store_data"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("TranscriptVectorStore initialized with all-MiniLM-L6-v2 embeddings")
        
        # Collection for transcript chunks
        self.collection_name = "earnings_transcripts"
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
        except Exception:
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Earnings call transcript chunks for semantic search"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
        
        return collection
    
    def add_transcript(self, transcript_text: str, company_symbol: str, 
                      transcript_date: str, source_info: Dict = None) -> int:
        """
        Add transcript to vector store by chunking and embedding
        
        Returns: Number of chunks added
        """
        # Create unique document ID
        doc_id = f"{company_symbol}_{transcript_date}"
        doc_hash = hashlib.md5(transcript_text.encode()).hexdigest()[:8]
        
        # Check if already exists
        try:
            existing = self.collection.get(ids=[f"{doc_id}_{doc_hash}_0"])
            if existing['ids']:
                logger.info(f"Transcript already exists: {doc_id}")
                return 0
        except Exception:
            pass  # Document doesn't exist, proceed with adding
        
        # Chunk transcript into manageable pieces
        chunks = self._chunk_transcript(transcript_text, company_symbol, transcript_date)
        logger.info(f"Created {len(chunks)} chunks from transcript")
        
        # Generate embeddings
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedding_model.encode(chunk_texts).tolist()
        
        # Prepare data for ChromaDB
        ids = [f"{doc_id}_{doc_hash}_{i}" for i in range(len(chunks))]
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            metadata = {
                'company_symbol': company_symbol,
                'transcript_date': transcript_date,
                'chunk_index': i,
                'chunk_type': chunk['type'],
                'speaker': chunk.get('speaker', 'unknown'),
                'doc_hash': doc_hash
            }
            if source_info:
                metadata.update(source_info)
            metadatas.append(metadata)
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=chunk_texts,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(chunks)} chunks to vector store for {doc_id}")
        return len(chunks)
    
    def _chunk_transcript(self, transcript: str, company: str, date: str) -> List[Dict]:
        """
        Intelligent chunking of transcript into meaningful segments
        """
        chunks = []
        lines = transcript.split('\n')
        current_chunk = []
        current_speaker = None
        chunk_type = 'general'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect speaker changes (common patterns in transcripts)
            speaker_patterns = [
                'Operator:', 'CEO:', 'CFO:', 'Analyst:', 'Management:',
                ':', ' - ', 'Question:', 'Answer:'
            ]
            
            is_speaker_line = any(pattern in line for pattern in speaker_patterns)
            
            # Detect section changes
            section_keywords = [
                'financial highlights', 'business update', 'outlook', 
                'guidance', 'q&a', 'questions', 'closing remarks'
            ]
            
            is_section_change = any(keyword in line.lower() for keyword in section_keywords)
            
            # Create chunk when speaker changes or reaches max size
            if (is_speaker_line or is_section_change or len(current_chunk) > 15) and current_chunk:
                chunk_text = ' '.join(current_chunk)
                if len(chunk_text) > 100:  # Only add substantial chunks
                    chunks.append({
                        'text': chunk_text,
                        'type': self._classify_chunk_type(chunk_text),
                        'speaker': current_speaker or 'unknown'
                    })
                current_chunk = []
            
            # Update speaker and add line to current chunk
            if is_speaker_line:
                current_speaker = line.split(':')[0] if ':' in line else 'speaker'
            
            current_chunk.append(line)
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text) > 100:
                chunks.append({
                    'text': chunk_text,
                    'type': self._classify_chunk_type(chunk_text),
                    'speaker': current_speaker or 'unknown'
                })
        
        return chunks
    
    def _classify_chunk_type(self, text: str) -> str:
        """Classify chunk based on content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['outlook', 'expect', 'forecast', 'guidance', 'going forward']):
            return 'outlook'
        elif any(word in text_lower for word in ['risk', 'challenge', 'headwind', 'concern', 'pressure']):
            return 'risk'
        elif any(word in text_lower for word in ['opportunity', 'growth', 'expansion', 'investment', 'launch']):
            return 'opportunity'
        elif any(word in text_lower for word in ['revenue', 'profit', 'margin', 'financial', 'performance']):
            return 'financial'
        else:
            return 'general'
        
    def search_transcripts(self, query: str, company_symbol: str = None, 
                          n_results: int = 5, min_similarity: float = 0.0) -> List[Dict]:  # Changed to 0.0
        """
        Semantic search across transcript chunks
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Build filter conditions
            where_filter = {}
            if company_symbol:
                where_filter["company_symbol"] = company_symbol
            
            # Search vector database
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter if where_filter else None,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Process and filter results with DEBUG logging
            relevant_chunks = []
            
            if results['ids'] and results['ids'][0]:  # Check if we got results
                logger.info(f"Raw search returned {len(results['ids'][0])} results")
                
                for i, chunk_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i]
                    similarity = 1 - distance  # Convert distance to similarity
                    
                    # DEBUG: Log similarity scores
                    if i < 3:  # Log top 3 for debugging
                        logger.info(f"Result {i+1}: similarity={similarity:.3f}, distance={distance:.3f}")
                    
                    if similarity >= min_similarity:
                        relevant_chunks.append({
                            'id': chunk_id,
                            'text': results['documents'][0][i],
                            'metadata': results['metadatas'][0][i],
                            'similarity': similarity,
                            'chunk_type': results['metadatas'][0][i].get('chunk_type', 'general'),
                            'speaker': results['metadatas'][0][i].get('speaker', 'unknown')
                        })
            
            logger.info(f"Found {len(relevant_chunks)} relevant chunks for query: '{query[:50]}...'")
            return relevant_chunks
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def search_by_category(self, category: str, company_symbol: str = None, 
                          n_results: int = 10) -> List[Dict]:
        """
        Search for chunks of specific category (outlook, risk, opportunity, etc.)
        """
        try:
            # FIXED: Simple where filter for ChromaDB
            where_filter = {"chunk_type": category}
            # Skip company filter for now to test basic functionality
            
            results = self.collection.get(
                where=where_filter,
                limit=n_results,
                include=['documents', 'metadatas']
            )
            
            chunks = []
            if results['ids']:
                for i, chunk_id in enumerate(results['ids']):
                    chunks.append({
                        'id': chunk_id,
                        'text': results['documents'][i],
                        'metadata': results['metadatas'][i],
                        'chunk_type': category,
                        'similarity': 1.0  # Perfect match by category
                    })
            
            logger.info(f"Found {len(chunks)} chunks for category: {category}")
            return chunks
            
        except Exception as e:
            logger.error(f"Category search failed: {e}")
            return []
    
    def get_management_outlook(self, company_symbol: str, n_results: int = 8) -> List[Dict]:
        """Get chunks specifically about management outlook and guidance"""
        outlook_queries = [
            "management outlook future guidance",
            "forward looking statements expectations", 
            "business outlook next quarter year",
            "growth expectations management guidance"
        ]
        
        all_chunks = []
        for query in outlook_queries:
            chunks = self.search_transcripts(
                query=query, 
                company_symbol=company_symbol, 
                n_results=n_results//2
            )
            all_chunks.extend(chunks)
        
        # Remove duplicates and sort by similarity
        unique_chunks = {chunk['id']: chunk for chunk in all_chunks}.values()
        sorted_chunks = sorted(unique_chunks, key=lambda x: x['similarity'], reverse=True)
        
        return sorted_chunks[:n_results]
    
    def get_risk_factors(self, company_symbol: str, n_results: int = 8) -> List[Dict]:
        """Get chunks about risks, challenges, and concerns"""
        risk_queries = [
            "risks challenges headwinds concerns",
            "competitive pressure market challenges",
            "regulatory risks compliance issues",
            "economic uncertainty market volatility"
        ]
        
        all_chunks = []
        for query in risk_queries:
            chunks = self.search_transcripts(
                query=query,
                company_symbol=company_symbol,
                n_results=n_results//2
            )
            all_chunks.extend(chunks)
        
        # Remove duplicates and get top results
        unique_chunks = {chunk['id']: chunk for chunk in all_chunks}.values()
        sorted_chunks = sorted(unique_chunks, key=lambda x: x['similarity'], reverse=True)
        
        return sorted_chunks[:n_results]
    
    def get_growth_opportunities(self, company_symbol: str, n_results: int = 8) -> List[Dict]:
        """Get chunks about growth opportunities and investments"""
        opportunity_queries = [
            "growth opportunities expansion plans",
            "new markets investment opportunities", 
            "technology investments innovation",
            "strategic initiatives new services"
        ]
        
        all_chunks = []
        for query in opportunity_queries:
            chunks = self.search_transcripts(
                query=query,
                company_symbol=company_symbol,
                n_results=n_results//2
            )
            all_chunks.extend(chunks)
        
        # Remove duplicates and get top results  
        unique_chunks = {chunk['id']: chunk for chunk in all_chunks}.values()
        sorted_chunks = sorted(unique_chunks, key=lambda x: x['similarity'], reverse=True)
        
        return sorted_chunks[:n_results]
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the vector store collection"""
        try:
            count_result = self.collection.count()
            
            # Get sample of documents to analyze
            sample = self.collection.peek(limit=100)
            
            companies = set()
            chunk_types = {}
            dates = set()
            
            if sample['metadatas']:
                for metadata in sample['metadatas']:
                    companies.add(metadata.get('company_symbol', 'unknown'))
                    chunk_type = metadata.get('chunk_type', 'unknown')
                    chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
                    dates.add(metadata.get('transcript_date', 'unknown'))
            
            return {
                'total_chunks': count_result,
                'companies': list(companies),
                'chunk_types': chunk_types,
                'transcript_dates': list(dates),
                'collection_name': self.collection_name
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {'error': str(e)}