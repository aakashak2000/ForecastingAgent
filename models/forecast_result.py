from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from models.financial_metrics import FinancialMetrics
from models.qualitative_insights import QualitativeAnalysisResult
from models.market_data import MarketData, MarketContext

class ForecastResult(BaseModel):
    """
    Complete financial forecast combining all three analysis tools
    """
    company_symbol: str
    forecast_period: str
    
    # Data from all three tools
    financial_metrics: Optional[FinancialMetrics] = None
    qualitative_analysis: Optional[QualitativeAnalysisResult] = None
    market_data: Optional[MarketData] = None
    market_context: Optional[MarketContext] = None
    
    # Master forecast synthesis
    overall_outlook: str = Field(..., description="positive, neutral, negative")
    confidence_score: float = Field(..., description="Overall forecast confidence 0-1")
    key_drivers: List[str] = Field(default=[], description="Main factors driving the forecast")
    investment_recommendation: str = Field(..., description="buy, hold, sell")
    
    # Metadata
    success: bool = True
    processing_time: float = 0.0
    error_message: Optional[str] = None