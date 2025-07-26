from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class QualitativeInsight(BaseModel):
    """
    Single qualitative insight extracted from earnings transcripts
    """
    category: str = Field(..., description="Type of insight: outlook, risk, opportunity, sentiment")
    insight: str = Field(..., description="The actual insight or finding")
    confidence: float = Field(..., description="Confidence score 0-1")
    supporting_quotes: List[str] = Field(default=[], description="Direct quotes supporting this insight")
    source_context: Optional[str] = Field(None, description="Context about where this was found")

class ManagementSentiment(BaseModel):
    """
    Overall management sentiment analysis
    """
    overall_tone: str = Field(..., description="positive, neutral, negative, mixed")
    optimism_score: float = Field(..., description="0-1 scale of management optimism")
    key_themes: List[str] = Field(default=[], description="Main themes management emphasized")
    forward_looking_statements: List[str] = Field(default=[], description="Future guidance or predictions")

class QualitativeAnalysisResult(BaseModel):
    """
    Complete result from qualitative analysis of earnings transcripts
    """
    company_symbol: str
    analysis_period: str  # e.g., "Q1-2025"
    transcript_date: str
    
    # Core Analysis Results
    management_sentiment: ManagementSentiment
    business_outlook: List[QualitativeInsight]
    risk_factors: List[QualitativeInsight] 
    growth_opportunities: List[QualitativeInsight]
    
    # Metadata
    success: bool = True
    processing_time: float = 0.0
    source_documents: List[str] = Field(default=[], description="Source transcript files")
    error_message: Optional[str] = None
    
    # Analysis Quality Metrics
    total_insights: int = Field(0, description="Total number of insights extracted")
    average_confidence: float = Field(0.0, description="Average confidence across all insights")
    
    def get_high_confidence_insights(self, min_confidence: float = 0.7) -> List[QualitativeInsight]:
        """Return only high-confidence insights"""
        all_insights = self.business_outlook + self.risk_factors + self.growth_opportunities
        return [insight for insight in all_insights if insight.confidence >= min_confidence]
    
    def get_summary_dict(self) -> Dict[str, Any]:
        """Get summary for easy JSON serialization"""
        return {
            "company": self.company_symbol,
            "period": self.analysis_period,
            "sentiment_score": self.management_sentiment.optimism_score,
            "total_insights": self.total_insights,
            "high_confidence_insights": len(self.get_high_confidence_insights()),
            "key_themes": self.management_sentiment.key_themes[:3],  # Top 3 themes
            "outlook_insights": len(self.business_outlook),
            "risk_insights": len(self.risk_factors),
            "opportunity_insights": len(self.growth_opportunities)
        }