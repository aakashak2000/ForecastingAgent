# Financial Forecasting Agent

> AI-powered financial analysis system that generates comprehensive investment forecasts by combining quantitative metrics, qualitative insights, and live market data.

## Overview

The Financial Forecasting Agent automatically analyzes corporate financial documents, earnings call transcripts, and real-time market data to produce structured investment recommendations. Built for financial analysts, portfolio managers, and investment researchers who need data-driven insights for decision making.

### Key Features

- **Automated Data Extraction**: Downloads and processes quarterly financial reports from public sources
- **Intelligent Document Analysis**: Extracts key financial metrics (revenue, profit, margins) using AI
- **Qualitative Sentiment Analysis**: Analyzes earnings call transcripts for management outlook and themes
- **Live Market Integration**: Fetches real-time stock data with valuation analysis
- **Structured Forecasts**: Produces machine-readable JSON with investment recommendations
- **Enterprise Logging**: Tracks all requests and responses in MySQL database

## Quick Start

### Prerequisites

- Python 3.10+
- MySQL 8.0 (recommended) or SQLite (automatic fallback)
- Git

### 1. Installation

```bash
# Clone repository
git clone <repository-url>
cd financial-forecasting-agent

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your MySQL password (required)
# LLM API keys are optional - system uses Ollama by default
```

### 3. Database Setup

```bash
# Create MySQL database
mysql -u root -p -e "CREATE DATABASE financial_forecasting;"

# Optional: Install Ollama for local LLM (no API keys needed)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b
```

### 4. Start the API

```bash
uvicorn app.main:app --reload
```

### 5. Generate Forecast

```bash
curl -X POST 'http://localhost:8000/forecast' \
     -H 'Content-Type: application/json' \
     -d '{"company_symbol": "TCS", "forecast_period": "Q2-2025"}'
```

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                  │
│                  (REST API Endpoints)                  │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              FinancialForecastingAgent                 │
│              (Master Orchestrator)                     │
└─┬─────────────────┬─────────────────┬─────────────────┬─┘
  │                 │                 │                 │
┌─▼─────────────┐ ┌─▼─────────────┐ ┌─▼─────────────┐ ┌─▼──────┐
│FinancialData │ │QualitativeAn │ │ MarketData    │ │ MySQL  │
│ExtractorTool │ │alysisTool    │ │ Tool          │ │Database│
│              │ │              │ │               │ │        │
│• PDF Analysis│ │• RAG Search  │ │• Live Prices  │ │• Logs  │
│• LLM Parsing │ │• Transcripts │ │• Valuation    │ │• Stats │
└──────────────┘ └──────────────┘ └───────────────┘ └────────┘
```

### Data Flow

1. **Financial Extraction**: Downloads quarterly reports → Extracts financial tables → LLM parsing → Structured metrics
2. **Qualitative Analysis**: Downloads earnings transcripts → Vector embeddings → Semantic search → Management insights  
3. **Market Intelligence**: Yahoo Finance API → Live stock data → Valuation analysis → Market context
4. **Forecast Synthesis**: Combines all sources → LLM reasoning → Investment recommendation → JSON output

## API Reference

### Generate Forecast

**Endpoint**: `POST /forecast`

**Request**:
```json
{
  "company_symbol": "TCS",
  "forecast_period": "Q2-2025"
}
```

**Response**:
```json
{
  "company_symbol": "TCS",
  "investment_recommendation": "buy",
  "analyst_confidence": 0.85,
  "overall_outlook": "positive",
  "current_price": 3135.8,
  "target_price": 3606.17,
  "target_upside_percent": 15.0,
  "management_sentiment": "positive",
  "management_optimism_score": 0.8,
  "business_outlook_insights": [
    "Revenue growth expected to accelerate in next quarter",
    "Cost optimization initiatives showing positive results"
  ],
  "growth_opportunities": [
    "AI adoption driving new business opportunities",
    "Expansion in cloud services segment"
  ],
  "risk_factors": [
    "No significant risk factors identified in current analysis"
  ],
  "key_drivers": [
    "Strong financial fundamentals",
    "Positive management outlook", 
    "Favorable market positioning"
  ],
  "processing_time": 45.2,
  "generated_at": "2025-07-27T15:30:00Z"
}
```

### Response Field Guide

| Field | Type | Scale | Description |
|-------|------|-------|-------------|
| `analyst_confidence` | float | 0.0-1.0 | Overall forecast confidence. 0.0=very uncertain, 0.5=moderate, 0.8+=high confidence |
| `management_optimism_score` | float | 0.0-1.0 | Management sentiment score. 0.0=very pessimistic, 0.5=neutral, 1.0=very optimistic |
| `investment_recommendation` | string | buy/hold/sell | Investment action based on analysis |
| `overall_outlook` | string | positive/neutral/negative | General business outlook |
| `target_upside_percent` | float | percentage | Expected price appreciation (only for "buy" recommendations) |
```

### Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-27T15:30:00Z",
  "components": {
    "agent": "operational",
    "database": "operational", 
    "market_data": "operational"
  }
}
```

## Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `MYSQL_HOST` | Yes | MySQL server host | `localhost` |
| `MYSQL_USER` | Yes | MySQL username | `root` |
| `MYSQL_PASSWORD` | Yes | MySQL password | - |
| `MYSQL_DATABASE` | Yes | Database name | `financial_forecasting` |
| `OPENAI_API_KEY` | No | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | No | Anthropic API key | - |
| `HUGGINGFACE_API_TOKEN` | No | HuggingFace token | - |
| `LOG_LEVEL` | No | Logging level | `INFO` |

### LLM Providers

The system automatically selects the best available LLM provider:

1. **Ollama** (Local, no API key needed) - Default choice
2. **OpenAI** (Premium, requires API key) - High quality responses  
3. **Anthropic** (Premium, requires API key) - Advanced reasoning
4. **Hugging Face** (Free tier available) - Backup option

## Supported Companies

The system works with any NSE-listed Indian company:

- **TCS** (Tata Consultancy Services)
- **INFY** (Infosys) 
- **RELIANCE** (Reliance Industries)
- **HDFCBANK** (HDFC Bank)
- **WIPRO** (Wipro Technologies)
- And 1000+ other NSE companies

## Production Deployment

### Database Setup

```sql
-- Create production database
CREATE DATABASE financial_forecasting;
CREATE USER 'forecast_user'@'%' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON financial_forecasting.* TO 'forecast_user'@'%';
FLUSH PRIVILEGES;
```

### Environment Configuration

```bash
# Production .env
MYSQL_HOST=your-db-host.com
MYSQL_USER=forecast_user
MYSQL_PASSWORD=secure_password
MYSQL_DATABASE=financial_forecasting

# Add API keys for better performance
OPENAI_API_KEY=sk-your-openai-key
LOG_LEVEL=WARNING
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Performance Optimizations

- **Caching**: Implement Redis for market data caching
- **Load Balancing**: Use nginx for multiple instances
- **Database**: Configure MySQL connection pooling
- **Monitoring**: Add Prometheus metrics and health checks

## Error Handling & Data Quality

The system includes comprehensive error handling and graceful degradation:

### Data Availability
- **Full Analysis**: When all 3 data sources are available (financial reports, transcripts, market data)
- **Partial Analysis**: When some data sources fail, analysis continues with available data
- **Professional Fallbacks**: Empty lists are replaced with explanatory messages:
  - `"No significant risk factors identified in current analysis"`
  - `"Business outlook analysis pending - limited transcript data available"`

### Data Source Failures
- **Financial Data Unavailable**: Uses market data and qualitative analysis only
- **Transcript Data Limited**: Relies on financial metrics and market context  
- **Market Data Offline**: Continues with financial and qualitative analysis

### LLM Provider Fallback
- **Ollama** (Local, primary) → **OpenAI** (API) → **Anthropic** (API) → **Hugging Face** (Free)
- Automatic provider switching ensures system reliability

### Database Resilience
- **MySQL Preferred**: Full logging and analytics
- **SQLite Fallback**: Automatic fallback when MySQL unavailable
- **Graceful Degradation**: API continues working even if logging fails

## Security Considerations

- **API Authentication**: Add JWT tokens for production use
- **Input Validation**: All inputs are validated and sanitized
- **SQL Injection**: Uses parameterized queries and ORM
- **Data Privacy**: No sensitive financial data is stored permanently

## Monitoring and Observability

### Logs

```bash
# View application logs
tail -f /var/log/forecast-agent/app.log

# Database query logs
SELECT COUNT(*) FROM forecast_requests WHERE created_at > NOW() - INTERVAL 1 DAY;
```

### Metrics

- **Request Rate**: Average requests per minute
- **Processing Time**: 95th percentile response times
- **Success Rate**: Percentage of successful forecasts
- **Data Quality**: Confidence scores and source availability

## Technical Stack

- **Backend**: FastAPI with async support
- **AI Framework**: LangChain for agent orchestration  
- **Database**: MySQL 8.0 with SQLAlchemy ORM
- **Vector Store**: ChromaDB with sentence-transformers
- **Document Processing**: pdfplumber for financial reports
- **Market Data**: Yahoo Finance API integration
- **LLM Support**: Ollama, OpenAI, Anthropic, Hugging Face

## License

Private commercial software - All rights reserved.

## Support

For technical support or feature requests, please contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: July 2025