from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.api.routes import router
from app.database import init_database
from agent.orchestrator import FinancialForecastingAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent instance (initialized once at startup)
agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global agent
    
    # Startup - initialize everything once
    logger.info("🚀 Starting Financial Forecasting Agent...")
    
    # Initialize database
    await init_database()
    
    # Initialize agent and all tools ONCE at startup
    logger.info("🔧 Initializing AI agent and tools (sentence transformers, vector store, etc.)...")
    agent = FinancialForecastingAgent()
    logger.info("✅ Agent and tools ready - requests will now be fast!")
    
    logger.info("✅ Financial Forecasting Agent started successfully")
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down Financial Forecasting Agent...")

# Create FastAPI app
app = FastAPI(
    title="Financial Forecasting Agent",
    description="AI-powered financial analysis combining market data, earnings transcripts, and quantitative metrics",
    version="1.0.0",
    lifespan=lifespan
)

# Include routes
app.include_router(router)

@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "Financial Forecasting Agent",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": ["/forecast", "/health"]
    }

def get_agent() -> FinancialForecastingAgent:
    """Get the global agent instance"""
    if agent is None:
        raise RuntimeError("Agent not initialized - server startup may have failed")
    return agent