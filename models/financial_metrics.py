from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class FinancialMetrics(BaseModel):
    """
    Structured financial metrics extracted from quarterly/annual reports
    """
    company_symbol: str
    report_period: str  # e.g., "FY2025", "Q1-2025"
    currency: str = "INR"  # Default to Indian Rupees
    
    # Core Revenue Metrics (in Crores)
    total_revenue: Optional[float] = Field(None, description="Total Revenue/Income")
    net_profit: Optional[float] = Field(None, description="Net Profit After Tax")
    operating_profit: Optional[float] = Field(None, description="Operating Profit/EBIT")
    
    # Margins (in percentage)
    operating_margin: Optional[float] = Field(None, description="Operating Margin %")
    net_margin: Optional[float] = Field(None, description="Net Profit Margin %")
    
    # Additional Context
    extraction_confidence: float = Field(0.0, description="Confidence score 0-1")
    raw_source: Optional[str] = Field(None, description="Raw text that was parsed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FinancialExtractionResult(BaseModel):
    """
    Complete result from financial data extraction process
    """
    success: bool
    metrics: Optional[FinancialMetrics] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0
    source_file: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy JSON serialization"""
        return self.dict(exclude_none=True)
