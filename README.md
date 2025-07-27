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

#### MySQL Setup (Recommended)

**Install MySQL:**
```bash
# macOS
brew install mysql
brew services start mysql

# Ubuntu/Linux
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql

# Windows
# Download from https://dev.mysql.com/downloads/mysql/
```

**Configure MySQL:**
```bash
# Secure installation
mysql_secure_installation

# Create database and user
mysql -u root -p
```

**In MySQL prompt:**
```sql
CREATE DATABASE financial_forecasting;
CREATE USER 'forecast_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON financial_forecasting.* TO 'forecast_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**Update .env with your credentials:**
```bash
MYSQL_HOST=localhost
MYSQL_USER=forecast_user
MYSQL_PASSWORD=your_secure_password
MYSQL_DATABASE=financial_forecasting
```

#### LLM Provider Setup

The system supports multiple LLM providers with automatic fallback. Choose your preferred option:

**Option 1: Ollama (Recommended - No API Keys Needed)**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Download model (in another terminal)
ollama pull llama3.1:8b

# Verify installation
ollama list
```

**Option 2: OpenAI (Premium)**
```bash
# Get API key from https://platform.openai.com/api-keys
# Add to .env:
OPENAI_API_KEY=sk-your-openai-key-here
```

**Option 3: Anthropic Claude (Premium)**
```bash
# Get API key from https://console.anthropic.com/
# Add to .env:
ANTHROPIC_API_KEY=your-anthropic-key-here
```

**Option 4: Hugging Face (Free Tier Available)**
```bash
# Get token from https://huggingface.co/settings/tokens
# Add to .env:
HUGGINGFACE_API_TOKEN=your-hf-token-here
```

**LLM Provider Priority:**
The system automatically tries providers in this order:
1. **Ollama** (if available) - No API costs
2. **OpenAI** (if API key provided) - Best performance  
3. **Anthropic** (if API key provided) - Advanced reasoning
4. **Hugging Face** (if token provided) - Free tier backup

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

Create `.env` file in project root:

```bash
# Database Configuration (Required)
MYSQL_HOST=localhost
MYSQL_USER=forecast_user
MYSQL_PASSWORD=your_secure_password
MYSQL_DATABASE=financial_forecasting

# LLM API Keys (Optional - system uses Ollama by default)
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
HUGGINGFACE_API_TOKEN=your-hf-token-here

# Application Settings
LOG_LEVEL=INFO
```

### Configuration Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `MYSQL_HOST` | Yes | MySQL server host | `localhost` |
| `MYSQL_USER` | Yes | MySQL username | `forecast_user` |
| `MYSQL_PASSWORD` | Yes | MySQL password | `secure_password123` |
| `MYSQL_DATABASE` | Yes | Database name | `financial_forecasting` |
| `OPENAI_API_KEY` | No | OpenAI API key | `sk-proj-...` |
| `ANTHROPIC_API_KEY` | No | Anthropic API key | `sk-ant-...` |
| `HUGGINGFACE_API_TOKEN` | No | HuggingFace token | `hf_...` |
| `LOG_LEVEL` | No | Logging level | `INFO` |

### LLM Provider Selection

The system automatically selects the best available LLM provider:

1. **Ollama** (Local, no API key needed)
   - ✅ Free and private
   - ✅ No rate limits
   - ✅ Works offline
   - ❌ Requires local resources

2. **OpenAI** (Premium, requires API key)
   - ✅ High quality responses
   - ✅ Fast processing
   - ❌ API costs apply
   - ❌ Internet required

3. **Anthropic** (Premium, requires API key)
   - ✅ Advanced reasoning
   - ✅ Long context support
   - ❌ API costs apply
   - ❌ Internet required

4. **Hugging Face** (Free tier available)
   - ✅ Free tier available
   - ✅ Various models
   - ❌ Rate limits on free tier
   - ❌ Internet required

## Troubleshooting

### Common Setup Issues

**1. MySQL Connection Failed**
```bash
ERROR: MySQL connection failed: Access denied for user 'root'@'localhost'
```
**Solution:**
- Verify MySQL is running: `brew services list | grep mysql` (macOS)
- Check password in `.env` matches MySQL password
- Ensure database exists: `mysql -u root -p -e "SHOW DATABASES;"`

**2. Ollama Not Found**
```bash
ERROR: No LLM providers available
```
**Solution:**
```bash
# Check if Ollama is running
ollama list

# If not installed
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b

# Start Ollama service
ollama serve
```

**3. PDF Download Fails**
```bash
WARNING: Failed to download PDF
```
**Solution:**
- Check internet connection
- Some PDFs may be temporarily unavailable
- System will continue with available data sources

**4. Port Already in Use**
```bash
ERROR: [Errno 48] Address already in use
```
**Solution:**
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --port 8001
```

### Performance Optimization

**For Better Performance:**
- Use **Ollama with llama3.1:8b** for fastest local processing
- Add **OpenAI API key** for best quality responses
- Ensure **MySQL** is properly indexed (automatic)
- Use **SSD storage** for faster PDF processing

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

MIT License - see [LICENSE](LICENSE) file for details.

## Support

For technical support or feature requests, please contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: July 2025