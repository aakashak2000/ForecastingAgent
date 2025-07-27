import re
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
    Enhanced vector storage and semantic search for earnings call transcripts
    """
    
    def __init__(self, persist_directory: str = "data/vector_store"):
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
        Add transcript to vector store with enhanced chunking and quality control
        
        Returns: Number of chunks added
        """
        # Validate input quality
        if len(transcript_text) < 2000:
            logger.warning(f"Transcript too short for {company_symbol}: {len(transcript_text)} chars")
            return 0
        
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
        
        # Enhanced chunking for better retrieval
        chunks = self._enhanced_transcript_chunking(transcript_text, company_symbol, transcript_date)
        
        if not chunks:
            logger.warning(f"No quality chunks created from transcript for {company_symbol}")
            return 0
        
        logger.info(f"Created {len(chunks)} quality chunks from transcript")
        
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
                'doc_hash': doc_hash,
                'quality_score': chunk.get('quality_score', 0.5)
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
        
        logger.info(f"Added {len(chunks)} quality chunks to vector store for {doc_id}")
        return len(chunks)
    
    def _enhanced_transcript_chunking(self, transcript: str, company: str, date: str) -> List[Dict]:
        """Enhanced intelligent chunking that works with poorly formatted text"""
        chunks = []
        
        # Clean text but preserve structure
        cleaned_text = transcript.replace('\n\n', ' [PARA] ').replace('\n', ' ')
        
        # For single-line content, split by sentences and speaker patterns
        if len(cleaned_text.split('\n')) < 10:  # Poorly formatted text
            # Split by speaker patterns and key phrases
            split_patterns = [
                r'(?i)(CEO|CFO|Analyst|Moderator|Management|Mr\.|Ms\.|Operator)[\s:]+',
                r'(?i)(Question|Answer|Thank you|Good [morning|evening])',
                r'(?i)(Moving on|Next question|Let me|I would like)',
                r'\. [A-Z]',  # Sentence boundaries
            ]
            
            # Create chunks of reasonable size (500-1500 characters)
            chunk_size = 800
            words = cleaned_text.split()
            current_chunk = []
            
            for word in words:
                current_chunk.append(word)
                chunk_text = ' '.join(current_chunk)
                
                # Create chunk when it reaches good size or finds natural break
                if len(chunk_text) > chunk_size:
                    if self._is_quality_chunk(chunk_text):
                        chunk_info = {
                            'text': chunk_text,
                            'type': self._classify_chunk_content(chunk_text),
                            'speaker': 'Management',
                            'quality_score': self._calculate_chunk_quality(chunk_text)
                        }
                        chunks.append(chunk_info)
                    
                    current_chunk = current_chunk[-50:]  # Keep some overlap
            
            # Add final chunk
            if current_chunk:
                final_text = ' '.join(current_chunk)
                if self._is_quality_chunk(final_text):
                    chunks.append({
                        'text': final_text,
                        'type': self._classify_chunk_content(final_text),
                        'speaker': 'Management',
                        'quality_score': self._calculate_chunk_quality(final_text)
                    })
        
        # Sort by quality and return top chunks
        chunks.sort(key=lambda x: x['quality_score'], reverse=True)
        return chunks[:50]  # Reasonable number of chunks
    
    def _clean_transcript_text(self, text: str) -> str:
        """Clean and normalize transcript text"""
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common transcript artifacts
        text = re.sub(r'\[.*?\]', '', text)  # Remove bracketed content
        text = re.sub(r'\(.*?\)', '', text)  # Remove parenthetical content
        
        # Normalize speaker indicators
        text = re.sub(r'([A-Z][a-z]+ [A-Z][a-z]+):', r'\1 -', text)
        
        return text.strip()
    
    def _detect_speaker_change(self, line: str) -> bool:
        """Enhanced speaker detection"""
        speaker_patterns = [
            r'^[A-Z][a-z]+ [A-Z][a-z]+\s*[-:]',  # Name patterns
            r'^(CEO|CFO|Analyst|Operator|Management|Moderator)\s*[-:]',
            r'^[A-Z]{2,}\s*[-:]',  # Acronyms
        ]
        
        return any(re.match(pattern, line, re.IGNORECASE) for pattern in speaker_patterns)
    
    def _detect_section_change(self, line: str) -> bool:
        """Detect section changes in transcript"""
        section_keywords = [
            'financial highlights', 'business update', 'outlook', 'guidance',
            'q&a', 'questions', 'closing remarks', 'opening remarks',
            'financial results', 'performance review'
        ]
        
        line_lower = line.lower()
        return any(keyword in line_lower for keyword in section_keywords)
    
    def _extract_speaker(self, line: str) -> str:
        """Extract speaker name from line"""
        import re
        
        patterns = [
            r'^([A-Z][a-z]+ [A-Z][a-z]+)\s*[-:]',
            r'^([A-Z]{2,})\s*[-:]',
            r'^(CEO|CFO|Analyst|Operator|Management)\s*[-:]'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return 'Unknown'
    
    def _is_quality_chunk(self, text: str) -> bool:
        """Determine if chunk meets quality standards"""
        # MUCH more lenient length requirements
        if len(text) < 50:  # Was 150, now 50
            return False
        
        if len(text.split()) < 10:  # Was 20, now 10  
            return False
        
        # More lenient content quality
        financial_keywords = [
            'revenue', 'profit', 'growth', 'margin', 'outlook', 'guidance',
            'performance', 'business', 'quarter', 'year', 'expect', 'forecast',
            'TCS', 'company', 'management', 'client', 'cost', 'investment'  # Added more keywords
        ]
        
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in financial_keywords if keyword in text_lower)
        
        # Must contain at least 1 relevant keyword (was 2)
        return keyword_count >= 1
    
    def _classify_chunk_content(self, text: str) -> str:
        """Enhanced content classification"""
        text_lower = text.lower()
        
        # More precise classification
        outlook_indicators = ['outlook', 'expect', 'forecast', 'guidance', 'going forward', 'next quarter', 'future']
        risk_indicators = ['risk', 'challenge', 'headwind', 'concern', 'pressure', 'difficult', 'uncertain']
        opportunity_indicators = ['opportunity', 'growth', 'expansion', 'investment', 'launch', 'new', 'innovation']
        financial_indicators = ['revenue', 'profit', 'margin', 'cost', 'expense', 'earnings', 'performance']
        
        # Score each category
        outlook_score = sum(1 for word in outlook_indicators if word in text_lower)
        risk_score = sum(1 for word in risk_indicators if word in text_lower)
        opportunity_score = sum(1 for word in opportunity_indicators if word in text_lower)
        financial_score = sum(1 for word in financial_indicators if word in text_lower)
        
        # Return highest scoring category
        scores = {
            'outlook': outlook_score,
            'risk': risk_score,
            'opportunity': opportunity_score,
            'financial': financial_score
        }
        
        max_category = max(scores, key=scores.get)
        return max_category if scores[max_category] > 0 else 'general'
    
    def _calculate_chunk_quality(self, text: str) -> float:
        """Calculate quality score for chunk prioritization"""
        score = 0.0
        text_lower = text.lower()
        
        # Length bonus (optimal range)
        word_count = len(text.split())
        if 30 <= word_count <= 100:
            score += 0.3
        elif 20 <= word_count <= 150:
            score += 0.2
        
        # Financial relevance
        financial_terms = ['revenue', 'profit', 'growth', 'margin', 'outlook', 'guidance', 'performance']
        relevance_score = sum(1 for term in financial_terms if term in text_lower) / len(financial_terms)
        score += relevance_score * 0.4
        
        # Forward-looking content (valuable for forecasting)
        future_terms = ['expect', 'forecast', 'guidance', 'outlook', 'next', 'future', 'plan', 'will']
        future_score = sum(1 for term in future_terms if term in text_lower) / len(future_terms)
        score += future_score * 0.3
        
        return min(score, 1.0)  # Cap at 1.0
    
    def search_transcripts(self, query: str, company_symbol: str = None, 
                          n_results: int = 5, min_similarity: float = 0.1) -> List[Dict]:
        """
        Enhanced semantic search with quality filtering
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Build filter conditions
            where_filter = {}
            if company_symbol:
                where_filter["company_symbol"] = company_symbol
            
            # Search with larger initial results for quality filtering
            search_results = n_results * 3  # Get more results to filter
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=search_results,
                where=where_filter if where_filter else None,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Enhanced result processing and quality filtering
            relevant_chunks = []
            
            if results['ids'] and results['ids'][0]:
                logger.info(f"Raw search returned {len(results['ids'][0])} results")
                
                for i, chunk_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i]
                    similarity = 1 - distance
                    
                    # Quality-based filtering
                    metadata = results['metadatas'][0][i]
                    quality_score = metadata.get('quality_score', 0.5)

                    # Combined score: similarity + quality
                    combined_score = (similarity * 0.7) + (quality_score * 0.3)

                    # FIXED: Much lower thresholds for better retrieval
                    if similarity >= min_similarity and combined_score > 0.05:  # Was 0.4, now 0.2
                        relevant_chunks.append({
                            'id': chunk_id,
                            'text': results['documents'][0][i],
                            'metadata': metadata,
                            'similarity': similarity,
                            'quality_score': quality_score,
                            'combined_score': combined_score,
                            'chunk_type': metadata.get('chunk_type', 'general'),
                            'speaker': metadata.get('speaker', 'unknown')
                        })
            
            # Sort by combined score and return top results
            relevant_chunks.sort(key=lambda x: x['combined_score'], reverse=True)
            top_chunks = relevant_chunks[:n_results]
            
            logger.info(f"Enhanced search: {len(top_chunks)} quality chunks for '{query[:50]}...'")
            if top_chunks:
                logger.info(f"Best result: similarity={top_chunks[0]['similarity']:.3f}, quality={top_chunks[0]['quality_score']:.3f}")
            
            return top_chunks
            
        except Exception as e:
            logger.error(f"Enhanced search failed: {e}")
            return []
    
    def get_management_outlook(self, company_symbol: str, n_results: int = 8) -> List[Dict]:
        """Get enhanced management outlook with quality filtering"""
        outlook_queries = [
            "management outlook future guidance expectations",
            "forward looking statements business outlook",
            "next quarter growth expectations guidance",
            "future performance management expectations"
        ]
        
        all_chunks = []
        for query in outlook_queries:
            chunks = self.search_transcripts(
                query=query, 
                company_symbol=company_symbol, 
                n_results=n_results//2,
                min_similarity=0.0
            )
            all_chunks.extend(chunks)
        
        # Remove duplicates and sort by combined score
        unique_chunks = {chunk['id']: chunk for chunk in all_chunks}.values()
        sorted_chunks = sorted(unique_chunks, key=lambda x: x['combined_score'], reverse=True)
        
        return sorted_chunks[:n_results]
    
    def get_collection_stats(self) -> Dict:
        """Get enhanced statistics about the vector store collection"""
        try:
            count_result = self.collection.count()
            
            # Get sample of documents to analyze
            sample = self.collection.peek(limit=100)
            
            companies = set()
            chunk_types = {}
            dates = set()
            quality_scores = []
            
            if sample['metadatas']:
                for metadata in sample['metadatas']:
                    companies.add(metadata.get('company_symbol', 'unknown'))
                    chunk_type = metadata.get('chunk_type', 'unknown')
                    chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
                    dates.add(metadata.get('transcript_date', 'unknown'))
                    quality_scores.append(metadata.get('quality_score', 0.5))
            
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
            
            return {
                'total_chunks': count_result,
                'companies': list(companies),
                'chunk_types': chunk_types,
                'transcript_dates': list(dates),
                'collection_name': self.collection_name,
                'average_quality_score': round(avg_quality, 3),
                'quality_status': 'high' if avg_quality > 0.7 else 'medium' if avg_quality > 0.5 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Failed to get enhanced collection stats: {e}")
            return {'error': str(e)}

    def get_growth_opportunities(self, company_symbol: str, n_results: int = 6) -> List[Dict]:
        """Get growth opportunities from transcripts"""
        # Use the exact query we know works
        chunks = self.search_transcripts(
            query="growth opportunities",
            company_symbol=company_symbol, 
            n_results=n_results,
            min_similarity=-1.0  # Accept all results
        )
        return chunks

    def get_risk_factors(self, company_symbol: str, n_results: int = 6) -> List[Dict]:
        """Get risk factors from transcripts"""
        # Try simpler risk-related queries
        queries = ["pressure", "challenges", "costs"]
        
        all_chunks = []
        for query in queries:
            chunks = self.search_transcripts(
                query=query,
                company_symbol=company_symbol, 
                n_results=2,
                min_similarity=-1.0
            )
            all_chunks.extend(chunks)
        
        # Remove duplicates and return top results
        unique_chunks = {chunk['id']: chunk for chunk in all_chunks}.values()
        sorted_chunks = sorted(unique_chunks, key=lambda x: x.get('combined_score', 0), reverse=True)
        
        return sorted_chunks[:n_results]