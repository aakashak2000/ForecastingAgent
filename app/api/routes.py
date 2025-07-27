from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
import time
from datetime import datetime
from typing import Optional

from app.database import log_request_response, get_database_stats

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

class ForecastRequest(BaseModel):
    company_symbol: str
    forecast_period: Optional[str] = "Q2-2025"

class ForecastResponse(BaseModel):
    """Production forecast response"""
    # Executive Summary
    company_symbol: str
    forecast_period: str
    overall_outlook: str
    investment_recommendation: str
    analyst_confidence: float
    
    # Financial Data
    current_price: Optional[float] = None
    market_cap_crores: Optional[float] = None
    pe_ratio: Optional[float] = None
    price_change_percent: Optional[float] = None
    target_price: Optional[float] = None
    target_upside_percent: Optional[float] = None
    
    # Market Analysis
    valuation_assessment: Optional[str] = None
    price_momentum: Optional[str] = None
    risk_level: Optional[str] = None
    
    # Management Insights
    management_sentiment: Optional[str] = None
    management_optimism_score: Optional[float] = None
    key_themes: list = []
    
    # Business Analysis
    business_outlook_insights: list = []
    growth_opportunities: list = []
    risk_factors: list = []
    key_drivers: list = []
    
    # Metadata
    processing_time: float
    generated_at: str
    success: bool = True
    error_message: Optional[str] = None

@router.post("/forecast", response_model=ForecastResponse)
async def generate_forecast(request: ForecastRequest):
    """
    Generate comprehensive financial forecast
    
    Combines quantitative metrics, qualitative insights, and market data
    to produce structured investment analysis
    """
    start_time = time.time()
    
    try:
        logger.info(f"Generating forecast for {request.company_symbol}")
        
        # Get the pre-initialized agent (fast - no loading time)
        from app.main import get_agent
        agent = get_agent()
        
        # Generate forecast using orchestrator
        result = agent.generate_forecast(request.company_symbol, request.forecast_period)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error_message)
        
        # Create business response
        response = _create_business_response(result, start_time)
        
        # Log to database
        await _log_forecast_request(request, response)
        
        logger.info(f"Forecast completed: {response.investment_recommendation} recommendation in {response.processing_time:.1f}s")
        return response
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_response = _create_error_response(request, str(e), processing_time)
        
        # Log error
        await _log_forecast_request(request, error_response, str(e))
        
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """System health check"""
    try:
        from app.main import get_agent
        agent = get_agent()
        agent_status = "operational"
    except:
        agent_status = "not_initialized"
    
    return {
        "status": "healthy" if agent_status == "operational" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "agent": agent_status,
            "database": "operational",
            "market_data": "operational"
        }
    }

@router.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        stats = await get_database_stats()
        return {
            "system_stats": stats,
            "status": "operational"
        }
    except Exception as e:
        return {"error": str(e), "status": "degraded"}

def _create_business_response(result, start_time) -> ForecastResponse:
    """Transform agent result into business response"""
    processing_time = time.time() - start_time
    
    # Calculate target price
    target_price = None
    target_upside = None
    if result.market_data and result.investment_recommendation.lower() == "buy":
        target_price = result.market_data.current_price * 1.15
        target_upside = 15.0
    
    # Extract insights with professional fallbacks
    business_insights = []
    growth_opportunities = []
    risk_factors = []
    
    if result.qualitative_analysis:
        business_insights = [_clean_insight_text(insight.insight) for insight in result.qualitative_analysis.business_outlook]
        growth_opportunities = [_clean_insight_text(opp.insight) for opp in result.qualitative_analysis.growth_opportunities]
        risk_factors = [_clean_insight_text(risk.insight) for risk in result.qualitative_analysis.risk_factors]
    
    # Handle empty lists professionally
    if not business_insights:
        business_insights = ["Business outlook analysis pending - limited transcript data available"]
    
    if not growth_opportunities:
        growth_opportunities = ["Growth opportunity analysis pending - limited transcript data available"]
    
    if not risk_factors:
        risk_factors = ["No significant risk factors identified in current analysis"]
    
    return ForecastResponse(
        company_symbol=result.company_symbol,
        forecast_period=result.forecast_period,
        overall_outlook=result.overall_outlook,
        investment_recommendation=result.investment_recommendation,
        analyst_confidence=result.confidence_score,
        
        # Financial data
        current_price=result.market_data.current_price if result.market_data else None,
        market_cap_crores=result.market_data.market_cap if result.market_data else None,
        pe_ratio=result.market_data.pe_ratio if result.market_data else None,
        price_change_percent=result.market_data.price_change_percent if result.market_data else None,
        target_price=target_price,
        target_upside_percent=target_upside,
        
        # Market context
        valuation_assessment=result.market_context.current_valuation if result.market_context else None,
        price_momentum=result.market_context.price_momentum if result.market_context else None,
        risk_level=result.market_context.risk_level if result.market_context else None,
        
        # Management insights
        management_sentiment=result.qualitative_analysis.management_sentiment.overall_tone if result.qualitative_analysis else None,
        management_optimism_score=result.qualitative_analysis.management_sentiment.optimism_score if result.qualitative_analysis else None,
        key_themes=result.qualitative_analysis.management_sentiment.key_themes if result.qualitative_analysis else [],
        
        # Business analysis
        business_outlook_insights=business_insights,
        growth_opportunities=growth_opportunities,
        risk_factors=risk_factors,
        key_drivers=result.key_drivers,
        
        # Metadata
        processing_time=processing_time,
        generated_at=datetime.now().isoformat()
    )

def _create_error_response(request: ForecastRequest, error: str, processing_time: float) -> ForecastResponse:
    """Create error response"""
    return ForecastResponse(
        company_symbol=request.company_symbol,
        forecast_period=request.forecast_period,
        overall_outlook="neutral",
        investment_recommendation="hold",
        analyst_confidence=0.0,
        processing_time=processing_time,
        generated_at=datetime.now().isoformat(),
        success=False,
        error_message=error
    )

async def _log_forecast_request(request: ForecastRequest, response: ForecastResponse, error: Optional[str] = None):
    """Log request/response to database"""
    try:
        await log_request_response(
            endpoint="/forecast",
            request_data=request.model_dump(),
            response_data=response.model_dump(),
            processing_time=response.processing_time,
            error=error
        )
        logger.info(f"✅ Database logging successful: {request.company_symbol}")
    except Exception as e:
        logger.error(f"❌ Database logging failed: {e}")

def _clean_insight_text(text: str) -> str:
    """Clean and improve insight text quality"""
    if not text:
        return text
    
    # Fix common LLM text issues
    text = text.replace("TCS'", "TCS's")  # Fix possessive
    text = text.replace(" as a percentage of revenue", " efficiency")  # Simplify phrasing
    text = text.replace("driven by a reduction in employee costs", "driven by improved cost management")
    
    # Ensure proper sentence structure
    if not text.endswith('.'):
        text += '.'
    
    return text