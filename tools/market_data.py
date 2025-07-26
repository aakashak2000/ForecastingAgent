import logging
import yfinance as yf
from typing import Optional
from models.market_data import MarketData, MarketContext

logger = logging.getLogger(__name__)

class MarketDataTool:
    """
    Fetches live market data for Indian stocks using Yahoo Finance
    """
    
    def __init__(self):
        self.session = None
    
    def get_stock_data(self, company_symbol: str) -> Optional[MarketData]:
        """
        Fetch current market data for a company
        
        Input: "TCS" 
        Output: MarketData object with live price, P/E ratio, etc.
        """
        try:
            # Convert to Yahoo Finance format for Indian stocks
            yf_symbol = f"{company_symbol}.NS"  # .NS for NSE (National Stock Exchange)
            
            logger.info(f"Fetching market data for {yf_symbol}")
            
            # Get stock info
            stock = yf.Ticker(yf_symbol)
            info = stock.info
            
            # Get current price and basic metrics
            current_price = info.get('currentPrice', 0.0)
            if current_price == 0.0:
                current_price = info.get('regularMarketPrice', 0.0)
            
            # Create MarketData object
            market_data = MarketData(
                symbol=yf_symbol,
                current_price=current_price,
                price_change=info.get('regularMarketChange', 0.0),
                price_change_percent=info.get('regularMarketChangePercent', 0.0),
                volume=info.get('regularMarketVolume', 0),
                market_cap=info.get('marketCap', 0) / 10000000 if info.get('marketCap') else None,  # Convert to crores
                pe_ratio=info.get('trailingPE'),
                week_52_high=info.get('fiftyTwoWeekHigh', 0.0),
                week_52_low=info.get('fiftyTwoWeekLow', 0.0)
            )
            
            logger.info(f"Successfully fetched data: ₹{current_price}, P/E: {market_data.pe_ratio}")
            return market_data
            
        except Exception as e:
            logger.error(f"Failed to fetch market data for {company_symbol}: {e}")
            return None
        
    def analyze_market_context(self, market_data: MarketData) -> Optional[MarketContext]:
        """
        Analyze market data to provide valuation and momentum insights
        
        Input: MarketData object with price, P/E, etc.
        Output: MarketContext with intelligent analysis
        """
        try:
            from models.market_data import MarketContext
            
            # Calculate position in 52-week range
            price_range = market_data.week_52_high - market_data.week_52_low
            current_vs_high = ((market_data.week_52_high - market_data.current_price) / market_data.week_52_high) * 100
            current_vs_low = ((market_data.current_price - market_data.week_52_low) / market_data.week_52_low) * 100
            
            # Determine valuation based on P/E ratio (IT sector average ~25)
            if market_data.pe_ratio:
                if market_data.pe_ratio < 20:
                    valuation = "undervalued"
                elif market_data.pe_ratio > 30:
                    valuation = "overvalued"
                else:
                    valuation = "fairly_valued"
            else:
                valuation = "unknown"
            
            # Determine momentum from price change
            if market_data.price_change_percent > 1.0:
                momentum = "bullish"
            elif market_data.price_change_percent < -1.0:
                momentum = "bearish"
            else:
                momentum = "neutral"
            
            # Generate insights
            insights = []
            insights.append(f"Trading {current_vs_high:.0f}% below 52-week high")
            insights.append(f"Trading {current_vs_low:.0f}% above 52-week low")
            
            if market_data.pe_ratio:
                insights.append(f"P/E ratio of {market_data.pe_ratio:.1f} suggests {valuation} stock")
            
            # Risk assessment based on volatility and position
            if current_vs_high > 40:  # More than 40% below high
                risk_level = "medium"
            elif current_vs_low < 20:  # Close to 52-week low
                risk_level = "high"
            else:
                risk_level = "low"
            
            context = MarketContext(
                symbol=market_data.symbol,
                current_valuation=valuation,
                price_momentum=momentum,
                volatility_level="medium",  # Can be enhanced with more data
                key_observations=insights,
                risk_level=risk_level,
                price_vs_52w_high=current_vs_high,
                price_vs_52w_low=current_vs_low
            )
            
            logger.info(f"Market analysis: {valuation}, {momentum} momentum, {risk_level} risk")
            return context
            
        except Exception as e:
            logger.error(f"Market context analysis failed: {e}")
            return None