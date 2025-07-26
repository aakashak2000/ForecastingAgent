from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MarketData(BaseModel):
    """
    Live stock market data for a company
    """
    symbol: str
    current_price: float = Field(..., description="Current stock price")
    price_change: float = Field(..., description="Price change in currency")
    price_change_percent: float = Field(..., description="Price change percentage")
    volume: int = Field(..., description="Trading volume")
    market_cap: Optional[float] = Field(None, description="Market capitalization in crores")
    pe_ratio: Optional[float] = Field(None, description="Price to Earnings ratio")
    week_52_high: float = Field(..., description="52-week high price")
    week_52_low: float = Field(..., description="52-week low price")
    
    # Metadata
    currency: str = "INR"
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())

class MarketContext(BaseModel):
    """
    Market analysis and valuation context
    """
    symbol: str
    current_valuation: str = Field(..., description="undervalued, fairly_valued, overvalued")
    price_momentum: str = Field(..., description="bullish, neutral, bearish")
    volatility_level: str = Field(..., description="low, medium, high")
    
    # Analysis insights
    key_observations: List[str] = Field(default=[], description="Key market insights")
    risk_level: str = Field(..., description="low, medium, high")
    
    # Supporting data
    price_vs_52w_high: float = Field(..., description="How far from 52-week high (percentage)")
    price_vs_52w_low: float = Field(..., description="How far from 52-week low (percentage)")