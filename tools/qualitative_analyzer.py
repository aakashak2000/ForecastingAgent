import logging
import time
from typing import List, Dict, Optional

from models.qualitative_insights import (
    QualitativeInsight, 
    ManagementSentiment, 
    QualitativeAnalysisResult
)
from vector_store.transcript_vectorstore import TranscriptVectorStore
from app.llm_manager import LLMProviderManager

logger = logging.getLogger(__name__)

class QualitativeAnalysisTool:
    """
    Analyzes earnings call transcripts to extract structured qualitative insights
    """

    def __init__(self, vectorstore_dir: str = "data/vector_store"):
        self.vectorstore = TranscriptVectorStore(persist_directory=vectorstore_dir)
        self.llm_manager = LLMProviderManager()
        self.llm = None
    
    def analyze_transcripts(self, company_symbol: str, analysis_period: str = None) -> QualitativeAnalysisResult:
        """
        Main analysis method - extracts qualitative insights from transcripts
        
        Args:
            company_symbol: Company to analyze (e.g., "TCS")
            analysis_period: Period label (e.g., "Q1-2025")
            
        Returns: Complete qualitative analysis with structured insights
        """
        start_time = time.time()
        
        try:
            # Initialize LLM if needed
            if not self.llm:
                self.llm = self.llm_manager.get_llm()
                logger.info(f"Using LLM provider: {self.llm_manager.current_provider}")
            
            # Step 1: Get collection stats and validate data exists
            stats = self.vectorstore.get_collection_stats()
            if stats.get('total_chunks', 0) == 0:
                return self._create_error_result(
                    company_symbol, analysis_period,
                    "No transcript data found in vector store",
                    time.time() - start_time
                )
            
            logger.info(f"Analyzing {stats['total_chunks']} chunks for {company_symbol}")
            
            # Step 2: Extract different types of insights using vector search
            management_sentiment = self._analyze_management_sentiment(company_symbol)
            business_outlook = self._extract_business_outlook(company_symbol)
            risk_factors = self._extract_risk_factors(company_symbol)
            growth_opportunities = self._extract_growth_opportunities(company_symbol)
            
            # Step 3: Determine analysis period from transcript data
            if not analysis_period:
                analysis_period = self._determine_analysis_period(stats)
            
            # Step 4: Create comprehensive result
            processing_time = time.time() - start_time
            
            result = QualitativeAnalysisResult(
                company_symbol=company_symbol,
                analysis_period=analysis_period,
                transcript_date=stats.get('transcript_dates', ['Unknown'])[0],
                management_sentiment=management_sentiment,
                business_outlook=business_outlook,
                risk_factors=risk_factors,
                growth_opportunities=growth_opportunities,
                processing_time=processing_time,
                source_documents=[f"{company_symbol}_transcript"],
                total_insights=len(business_outlook) + len(risk_factors) + len(growth_opportunities),
                average_confidence=self._calculate_average_confidence(
                    business_outlook + risk_factors + growth_opportunities
                )
            )
            
            logger.info(f"Analysis completed: {result.total_insights} insights, "
                       f"avg confidence {result.average_confidence:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Qualitative analysis failed: {e}")
            return self._create_error_result(
                company_symbol, analysis_period, str(e), time.time() - start_time
            )
    
    def _analyze_management_sentiment(self, company_symbol: str) -> ManagementSentiment:
        """Analyze overall management tone and sentiment"""
        
        # Get management outlook chunks
        outlook_chunks = self.vectorstore.get_management_outlook(company_symbol, n_results=5)
        
        if not outlook_chunks:
            logger.warning("No management outlook chunks found")
            return ManagementSentiment(
                overall_tone="neutral",
                optimism_score=0.5,
                key_themes=[],
                forward_looking_statements=[]
            )
        
        # Combine relevant chunks for LLM analysis
        combined_text = self._combine_chunks_for_analysis(outlook_chunks, max_chunks=3)
        
        # Create sentiment analysis prompt
        prompt = self._create_sentiment_prompt(combined_text, company_symbol)
        
        # Get LLM analysis
        llm_response = self.llm.invoke(prompt)
        
        # Parse response into structured sentiment
        sentiment = self._parse_sentiment_response(llm_response)
        
        return sentiment
    
    def _extract_business_outlook(self, company_symbol: str) -> List[QualitativeInsight]:
        """Extract insights about business outlook and future guidance"""
        
        outlook_chunks = self.vectorstore.get_management_outlook(company_symbol, n_results=6)
        
        if not outlook_chunks:
            return []
        
        # Analyze in batches to get diverse insights
        insights = []
        for i in range(0, len(outlook_chunks), 2):
            batch_chunks = outlook_chunks[i:i+2]
            batch_text = self._combine_chunks_for_analysis(batch_chunks)
            
            prompt = self._create_insight_extraction_prompt(
                batch_text, "business_outlook", company_symbol
            )
            
            llm_response = self.llm.invoke(prompt)
            batch_insights = self._parse_insights_response(llm_response, "outlook")
            insights.extend(batch_insights)
        
        return insights[:5]  # Return top 5 insights
    
    def _extract_risk_factors(self, company_symbol: str) -> List[QualitativeInsight]:
        """Extract insights about risks and challenges"""
        
        risk_chunks = self.vectorstore.get_risk_factors(company_symbol, n_results=6)
        
        if not risk_chunks:
            return []
        
        insights = []
        for i in range(0, len(risk_chunks), 2):
            batch_chunks = risk_chunks[i:i+2]
            batch_text = self._combine_chunks_for_analysis(batch_chunks)
            
            prompt = self._create_insight_extraction_prompt(
                batch_text, "risk_factors", company_symbol
            )
            
            llm_response = self.llm.invoke(prompt)
            batch_insights = self._parse_insights_response(llm_response, "risk")
            insights.extend(batch_insights)
        
        return insights[:4]  # Return top 4 risk insights
    
    def _extract_growth_opportunities(self, company_symbol: str) -> List[QualitativeInsight]:
        """Extract insights about growth opportunities and investments"""
        
        opportunity_chunks = self.vectorstore.get_growth_opportunities(company_symbol, n_results=6)
        
        if not opportunity_chunks:
            return []
        
        insights = []
        for i in range(0, len(opportunity_chunks), 2):
            batch_chunks = opportunity_chunks[i:i+2]
            batch_text = self._combine_chunks_for_analysis(batch_chunks)
            
            prompt = self._create_insight_extraction_prompt(
                batch_text, "growth_opportunities", company_symbol
            )
            
            llm_response = self.llm.invoke(prompt)
            batch_insights = self._parse_insights_response(llm_response, "opportunity")
            insights.extend(batch_insights)
        
        return insights[:4]  # Return top 4 opportunity insights
    
    def _combine_chunks_for_analysis(self, chunks: List[Dict], max_chunks: int = 3) -> str:
        """Combine multiple chunks into analysis-ready text"""
        if not chunks:
            return ""
        
        combined_parts = []
        for i, chunk in enumerate(chunks[:max_chunks]):
            speaker = chunk.get('speaker', 'Speaker')
            chunk_type = chunk.get('chunk_type', 'general')
            similarity = chunk.get('similarity', 0)
            
            part_header = f"\n--- EXCERPT {i+1} [{chunk_type.upper()}] (Relevance: {similarity:.2f}) ---"
            part_content = f"{speaker}: {chunk['text']}"
            
            combined_parts.append(part_header)
            combined_parts.append(part_content)
        
        return '\n'.join(combined_parts)
    
    def _create_sentiment_prompt(self, transcript_text: str, company_symbol: str) -> str:
        """Create prompt for management sentiment analysis"""
        
        prompt = f"""
You are analyzing management sentiment from {company_symbol} earnings call transcript excerpts.

TRANSCRIPT EXCERPTS:
{transcript_text}

TASK: Analyze the overall management sentiment and tone. 

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "overall_tone": "<positive|negative|neutral|mixed>",
    "optimism_score": <0.0_to_1.0>,
    "key_themes": ["theme1", "theme2", "theme3"],
    "forward_looking_statements": ["statement1", "statement2"],
    "confidence": <0.0_to_1.0>
}}

GUIDELINES:
- overall_tone: positive (optimistic), negative (pessimistic), neutral (balanced), mixed (both positive/negative)
- optimism_score: 0.0 (very pessimistic) to 1.0 (very optimistic)
- key_themes: Main topics management emphasized (max 5)
- forward_looking_statements: Future guidance or predictions (max 3)
- confidence: How confident you are in this analysis
"""
        
        return prompt.strip()
    
    def _parse_sentiment_response(self, llm_response: str) -> ManagementSentiment:
        """Parse LLM sentiment analysis response"""
        import json
        import re
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                sentiment = ManagementSentiment(
                    overall_tone=parsed.get('overall_tone', 'neutral'),
                    optimism_score=float(parsed.get('optimism_score', 0.5)),
                    key_themes=parsed.get('key_themes', []),
                    forward_looking_statements=parsed.get('forward_looking_statements', [])
                )
                
                logger.info(f"Parsed sentiment: {sentiment.overall_tone}, optimism: {sentiment.optimism_score}")
                return sentiment
                
            else:
                logger.warning("No JSON found in sentiment response")
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse sentiment response: {e}")
        
        # Fallback sentiment
        return ManagementSentiment(
            overall_tone="neutral",
            optimism_score=0.5,
            key_themes=[],
            forward_looking_statements=[]
        )
    
    def _create_insight_extraction_prompt(self, transcript_text: str, 
                                        insight_type: str, company_symbol: str) -> str:
        """Create prompt for extracting specific types of insights"""
        
        type_descriptions = {
            "business_outlook": "business outlook, future guidance, growth expectations, and strategic direction",
            "risk_factors": "risks, challenges, headwinds, concerns, and potential obstacles",
            "growth_opportunities": "growth opportunities, expansion plans, new investments, and strategic initiatives"
        }
        
        description = type_descriptions.get(insight_type, "general business insights")
        
        prompt = f"""
You are extracting {description} from {company_symbol} earnings call transcript excerpts.

TRANSCRIPT EXCERPTS:
{transcript_text}

TASK: Extract 1-2 key insights about {description}.

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "insights": [
        {{
            "insight": "<clear, specific insight>",
            "confidence": <0.0_to_1.0>,
            "supporting_quote": "<exact quote from transcript>"
        }}
    ]
}}

GUIDELINES:
- insight: Specific, actionable insight (1-2 sentences)
- confidence: How confident you are this insight is accurate (0.0-1.0)
- supporting_quote: Direct quote from transcript that supports this insight
- Focus on concrete, specific information rather than generic statements
- Only include insights with confidence > 0.3
"""
        
        return prompt.strip()
    
    def _parse_insights_response(self, llm_response: str, category: str) -> List[QualitativeInsight]:
        """Parse LLM insights extraction response"""
        import json
        import re
        
        insights = []
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                for insight_data in parsed.get('insights', []):
                    if insight_data.get('confidence', 0) > 0.3:  # Only high-confidence insights
                        insight = QualitativeInsight(
                            category=category,
                            insight=insight_data.get('insight', ''),
                            confidence=float(insight_data.get('confidence', 0.5)),
                            supporting_quotes=[insight_data.get('supporting_quote', '')],
                            source_context=f"Earnings call transcript analysis"
                        )
                        insights.append(insight)
                
                logger.info(f"Extracted {len(insights)} {category} insights")
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse {category} insights: {e}")
        
        return insights
    
    def _determine_analysis_period(self, stats: Dict) -> str:
        """Determine analysis period from transcript data"""
        transcript_dates = stats.get('transcript_dates', [])
        if transcript_dates:
            date = transcript_dates[0]
            if 'jul' in date.lower() or '07' in date:
                return "Q1-2025"
            elif 'apr' in date.lower() or '04' in date:
                return "Q4-2024"
            elif 'jan' in date.lower() or '01' in date:
                return "Q3-2024"
        
        return "Unknown"
    
    def _calculate_average_confidence(self, insights: List[QualitativeInsight]) -> float:
        """Calculate average confidence across all insights"""
        if not insights:
            return 0.0
        
        total_confidence = sum(insight.confidence for insight in insights)
        return total_confidence / len(insights)
    
    def _create_error_result(self, company_symbol: str, analysis_period: str, 
                           error_message: str, processing_time: float) -> QualitativeAnalysisResult:
        """Create error result when analysis fails"""
        
        return QualitativeAnalysisResult(
            company_symbol=company_symbol,
            analysis_period=analysis_period or "Unknown",
            transcript_date="Unknown",
            management_sentiment=ManagementSentiment(
                overall_tone="neutral",
                optimism_score=0.5,
                key_themes=[],
                forward_looking_statements=[]
            ),
            business_outlook=[],
            risk_factors=[],
            growth_opportunities=[],
            success=False,
            error_message=error_message,
            processing_time=processing_time,
            source_documents=[],
            total_insights=0,
            average_confidence=0.0
        )