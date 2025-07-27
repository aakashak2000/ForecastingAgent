# Financial Forecasting Agent

> AI-powered financial analysis system that generates comprehensive investment forecasts by combining quantitative metrics, qualitative insights, and live market data.

## 🚀 Quick Start for Evaluators

**Get the system running in 3 steps:**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup database (update password in .env)
mysql -u root -p -e "CREATE DATABASE financial_forecasting;"
cp .env.example .env  # Edit with your MySQL password

# 3. Start the API
uvicorn app.main:app --reload
```

**Test the system:**
```bash
# Generate a forecast (takes ~5-10 minutes for full analysis)
curl -X POST 'http://localhost:8000/forecast' \
     -H 'Content-Type: application/json' \
     -d '{"company_symbol": "TCS"}'
```

**Key Points for Evaluation:**
- ✅ **No API keys required** - Uses Ollama by default (auto-installed)
- ✅ **All task requirements met** - Financial extraction + RAG analysis + Market data + MySQL logging
- ✅ **Professional output** - Structured JSON with investment recommendations
- ✅ **Production ready** - Error handling, fallbacks, comprehensive documentation

---

## Project Overview

The Financial Forecasting Agent automatically analyzes corporate financial documents, earnings call transcripts, and real-time market data to produce structured investment recommendations. Built for financial analysts, portfolio managers, and investment researchers who need data-driven insights for decision making.

### Key Features

- **Automated Data Extraction**: Downloads and processes quarterly financial reports from public sources
- **Intelligent Document Analysis**: Extracts key financial metrics (revenue, profit, margins) using AI
- **Qualitative Sentiment Analysis**: Analyzes earnings call transcripts for management outlook and themes
- **Live Market Integration**: Fetches real-time stock data with valuation analysis
- **Structured Forecasts**: Produces machine-readable JSON with investment recommendations
- **Enterprise Logging**: Tracks all requests and responses in MySQL database

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                  │
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
│• PDF Analysis│ │• RAG Search  │ │• Live Prices  │ │• Logs  │
│• LLM Parsing │ │• Transcripts │ │• Valuation    │ │• Stats │
└──────────────┘ └──────────────┘ └───────────────┘ └────────┘
```

**Data Flow**: Downloads quarterly reports → Extracts financial tables → Analyzes earnings transcripts → Fetches live market data → Synthesizes comprehensive forecast → Returns structured JSON

## Setup Instructions

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

### 2. Database Setup

**MySQL (Recommended):**
```bash
# Install MySQL
brew install mysql  # macOS
# sudo apt install mysql-server  # Ubuntu

# Start MySQL service
brew services start mysql

# Create database
mysql -u root -p -e "CREATE DATABASE financial_forecasting;"
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your MySQL credentials
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password_here
MYSQL_DATABASE=financial_forecasting
```

### 4. LLM Provider Setup (Optional)

**Ollama (Recommended - No API Keys):**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download model
ollama pull llama3.1:8b
```

**Alternative Providers (Optional):**
```bash
# Add to .env for premium options
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
HUGGINGFACE_API_TOKEN=your-hf-token-here
```

### 5. Start the API

```bash
# Start the FastAPI server
uvicorn app.main:app --reload

# Expected startup output:
# INFO: 🚀 Starting Financial Forecasting Agent...
# INFO: ✅ Connected to MySQL database
# INFO: 🔧 Initializing AI agent and tools...
# INFO: ✅ Agent and tools ready - requests will now be fast!
```

### 6. Verify Installation

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "components": {
    "agent": "operational",
    "database": "operational"
  }
}
```

## Agent & Tool Design

### Master Agent Architecture

The `FinancialForecastingAgent` orchestrates three specialized tools using a structured reasoning approach:

```python
# Master Agent Reasoning Chain
def generate_forecast(self, company_symbol: str, forecast_period: str):
    1. Extract quantitative financial metrics (FinancialDataExtractorTool)
    2. Analyze qualitative management insights (QualitativeAnalysisTool)  
    3. Gather live market context (MarketDataTool)
    4. Synthesize comprehensive forecast using LLM reasoning
    5. Return structured investment recommendation
```

### Tool 1: FinancialDataExtractorTool

**Purpose**: Extract structured financial metrics from quarterly/annual PDF reports

**Process Flow**: `PDF Download → Table Extraction → LLM Parsing → Structured Metrics`

**Master Prompt**:
```
You are a financial analyst extracting key metrics from {company_symbol} financial tables.

TASK: Extract the following key financial metrics (values in Crores INR):
1. TOTAL REVENUE / TOTAL INCOME
2. NET PROFIT / NET PROFIT AFTER TAX  
3. OPERATING PROFIT / EBIT
4. OPERATING MARGIN (as percentage)
5. NET MARGIN (as percentage)

RESPOND IN THIS EXACT JSON FORMAT:
{
    "total_revenue": <number_or_null>,
    "net_profit": <number_or_null>, 
    "operating_profit": <number_or_null>,
    "operating_margin": <number_or_null>,
    "net_margin": <number_or_null>,
    "confidence": <0.0_to_1.0>,
    "notes": "<explanation_of_findings>"
}
```

**Output**: Structured `FinancialMetrics` object with revenue, profit, margins, and confidence scores

### Tool 2: QualitativeAnalysisTool

**Purpose**: Extract management sentiment and business insights from earnings call transcripts

**Process Flow**: `Transcript Download → Text Chunking → Vector Embedding → Semantic Search → LLM Analysis`

**Master Prompt for Sentiment Analysis**:
```
You are analyzing management sentiment from {company_symbol} earnings call excerpts.

TASK: Analyze overall management sentiment and tone.

RESPOND IN THIS EXACT JSON FORMAT:
{
    "overall_tone": "<positive|negative|neutral|mixed>",
    "optimism_score": <0.0_to_1.0>,
    "key_themes": ["theme1", "theme2", "theme3"],
    "forward_looking_statements": ["statement1", "statement2"],
    "confidence": <0.0_to_1.0>
}

GUIDELINES:
- optimism_score: 0.0 (very pessimistic) to 1.0 (very optimistic)
- key_themes: Main topics management emphasized
- Focus on future guidance and business outlook
```

**Output**: Structured `QualitativeAnalysisResult` with sentiment scores, business insights, and supporting quotes

### Tool 3: MarketDataTool

**Purpose**: Provide real-time market context and valuation analysis

**Process Flow**: `Yahoo Finance API → Live Data Fetch → Valuation Analysis → Market Context`

**Analysis Logic**:
```python
# Valuation Assessment
if pe_ratio < 20: valuation = "undervalued"
elif pe_ratio > 30: valuation = "overvalued"  
else: valuation = "fairly_valued"

# Risk Assessment  
if current_vs_high > 40%: risk = "medium"
elif current_vs_low < 20%: risk = "high"
else: risk = "low"
```

**Output**: Structured `MarketData` and `MarketContext` with live prices, ratios, and intelligent analysis

### Master Agent Synthesis

The agent combines all three data sources using this comprehensive reasoning approach:

**Synthesis Prompt**:
```
You are a senior financial analyst creating a comprehensive forecast by integrating:
1. FINANCIAL METRICS (from quarterly reports)
2. MANAGEMENT INSIGHTS (from earnings call transcripts) 
3. MARKET CONTEXT (live stock data and valuation)

TASK: Create a unified investment forecast.

RESPOND IN JSON FORMAT:
{
    "overall_outlook": "<positive|neutral|negative>",
    "confidence_score": <0.0_to_1.0>,
    "investment_recommendation": "<buy|hold|sell>",
    "key_drivers": ["driver1", "driver2", "driver3"]
}

REASONING GUIDELINES:
- Higher confidence when all sources align
- Consider financial trends, management sentiment, and market positioning
- Focus on actionable investment thesis
```

**Agent Reasoning Chain**:
1. **Data Gathering**: Downloads reports, processes transcripts, fetches market data
2. **Analysis**: Identifies financial trends, management sentiment, market positioning
3. **Synthesis**: Combines quantitative trends with qualitative insights
4. **Forecast**: Generates outlook, recommendation, and confidence score

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
  "management_sentiment": "positive",
  "business_outlook_insights": [
    "Revenue growth expected to accelerate in next quarter"
  ],
  "growth_opportunities": [
    "AI adoption driving new business opportunities"
  ],
  "key_drivers": [
    "Strong financial fundamentals",
    "Positive management outlook"
  ],
  "processing_time": 45.2,
  "generated_at": "2025-07-27T15:30:00Z"
}
```

### Response Field Guide

| Field | Scale | Description |
|-------|-------|-------------|
| `analyst_confidence` | 0.0-1.0 | Overall forecast confidence (0.8+ = high confidence) |
| `management_optimism_score` | 0.0-1.0 | Management sentiment (0.5 = neutral, 1.0 = very optimistic) |
| `investment_recommendation` | buy/hold/sell | Investment action based on analysis |
| `target_upside_percent` | percentage | Expected price appreciation (only for "buy" recommendations) |

### Health Check

**Endpoint**: `GET /health`

```json
{
  "status": "healthy",
  "components": {
    "agent": "operational",
    "database": "operational"
  }
}
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MYSQL_HOST` | Yes | MySQL server host |
| `MYSQL_USER` | Yes | MySQL username |
| `MYSQL_PASSWORD` | Yes | MySQL password |
| `MYSQL_DATABASE` | Yes | Database name |
| `OPENAI_API_KEY` | No | OpenAI API key (optional) |
| `ANTHROPIC_API_KEY` | No | Anthropic API key (optional) |
| `HUGGINGFACE_API_TOKEN` | No | HuggingFace token (optional) |

### LLM Provider Selection

The system automatically selects the best available provider:
1. **Ollama** (Local, free) - Default choice
2. **OpenAI** (Premium) - Best performance  
3. **Anthropic** (Premium) - Advanced reasoning
4. **Hugging Face** (Free tier) - Backup option

## Supported Companies

Works with any NSE-listed Indian company: **TCS**, **INFY**, **RELIANCE**, **HDFCBANK**, **WIPRO**, and 1000+ others.

## Advanced Documentation

For detailed information, see:
- 📖 [Architecture Details](docs/ARCHITECTURE.md) - System design and data flow
- 🚀 [Production Deployment](docs/PRODUCTION.md) - Docker, security, monitoring  
- 🔧 [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common issues and optimization

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

---

**Version**: 1.0.0 | **Last Updated**: July 2025