# Financial Forecasting Agent

An intelligent AI agent system that analyzes corporate financial documents and earnings transcripts to generate comprehensive business outlook forecasts. Built with FastAPI, LangChain, and multiple specialized AI tools for automated financial analysis.

## Project Overview

This system goes beyond traditional Q&A by autonomously discovering, analyzing, and synthesizing financial data from multiple sources to produce reasoned qualitative forecasts. The agent leverages specialized tools to extract quantitative metrics from quarterly reports and perform semantic analysis of earnings call transcripts.

### Key Capabilities

- **Automated Financial Data Extraction**: Processes quarterly financial reports to extract key metrics (revenue, profit, margins)
- **Qualitative Sentiment Analysis**: RAG-based analysis of earnings call transcripts for management outlook and themes
- **Live Market Intelligence**: Real-time stock data integration with valuation analysis
- **Multi-Source Synthesis**: Combines quantitative trends with qualitative insights for comprehensive forecasting
- **Structured Output Generation**: Produces machine-readable JSON forecasts with consistent schema
- **Enterprise Logging**: Full request tracking and tool execution logging to MySQL database

## Architecture

### Agent-Based Design

The system employs a multi-tool agent architecture where specialized tools handle distinct aspects of financial analysis:

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
│                  (REST API Endpoints)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                FinancialForecastingAgent                   │
│              (Master Orchestrator)                         │
└─┬─────────────────┬─────────────────┬─────────────────────┬─┘
  │                 │                 │                     │
┌─▼─────────────┐ ┌─▼─────────────┐ ┌─▼─────────────┐ ┌───▼──────┐
│FinancialData │ │QualitativeAn │ │ MarketData    │ │  MySQL   │
│ExtractorTool │ │alysisTool    │ │ Tool          │ │ Database │
│              │ │              │ │               │ │ Logging  │
│• PDF Analysis│ │• RAG Search  │ │• Live Prices  │ │          │
│• Table Extract│ │• Transcript  │ │• P/E Ratios   │ │          │
│• LLM Parsing │ │• Sentiment   │ │• Valuation    │ │          │
└──────────────┘ └──────────────┘ └───────────────┘ └──────────┘
```

### Tool Integration Flow

1. **FinancialDataExtractorTool**: Downloads and extracts financial metrics from quarterly reports
2. **QualitativeAnalysisTool**: Performs semantic search across earnings transcripts using vector embeddings
3. **MarketDataTool**: Fetches real-time market data and performs valuation analysis
4. **Agent Orchestrator**: Synthesizes insights using LLM reasoning to generate unified forecasts

## Agent & Tool Design

### 1. FinancialDataExtractorTool

**Purpose**: Extract structured financial metrics from PDF quarterly reports

**Process Flow**:
```
PDF Report → Table Extraction → LLM Parsing → Structured Metrics
```

**Key Components**:
- **PDFTableExtractor**: Uses pdfplumber to extract tables from financial PDFs
- **LLM Parser**: Interprets extracted tables to identify key financial metrics
- **Data Validation**: Ensures extracted numbers follow business logic rules

**Output Schema**:
```json
{
  "total_revenue": 48797.0,
  "net_profit": 19000.0,
  "operating_margin": 23.4,
  "extraction_confidence": 0.9
}
```

### 2. QualitativeAnalysisTool

**Purpose**: Extract management sentiment and business insights from earnings call transcripts

**Process Flow**:
```
Transcript Download → Text Chunking → Vector Embedding → Semantic Search → LLM Analysis
```

**Key Components**:
- **TranscriptVectorStore**: ChromaDB-based semantic search using sentence-transformers
- **Intelligent Chunking**: Segments transcripts by speaker and topic for better retrieval
- **Multi-Query Analysis**: Searches for outlook, risks, and opportunities separately

**Output Schema**:
```json
{
  "management_sentiment": {
    "overall_tone": "positive",
    "optimism_score": 0.8,
    "key_themes": ["cost optimization", "AI innovation"]
  },
  "business_outlook": [
    {
      "insight": "Employee costs to trend downwards towards 45% range",
      "confidence": 0.85,
      "supporting_quotes": ["..."]
    }
  ]
}
```

### 3. MarketDataTool

**Purpose**: Provide real-time market context and valuation analysis

**Process Flow**:
```
Yahoo Finance API → Live Data Fetch → Valuation Analysis → Market Context
```

**Key Features**:
- **Real-time Pricing**: Current stock price, volume, and daily changes
- **Valuation Metrics**: P/E ratios, market cap, 52-week range analysis
- **Risk Assessment**: Position-based risk evaluation and momentum analysis

**Output Schema**:
```json
{
  "current_price": 3135.8,
  "market_cap_crores": 1234382.6,
  "pe_ratio": 23.0,
  "valuation_assessment": "fairly_valued",
  "risk_level": "high"
}
```

### Master Agent Reasoning

The FinancialForecastingAgent employs a structured reasoning process:

**Core Prompt Strategy**:
```
You are a financial analyst creating a comprehensive forecast by combining:
1. Quantitative financial metrics (revenue, margins, growth trends)
2. Qualitative management insights (sentiment, outlook, guidance)  
3. Market context (valuation, momentum, risk positioning)

Synthesize this information into a unified investment thesis with:
- Overall outlook (positive/neutral/negative)
- Investment recommendation (buy/hold/sell)
- Confidence score based on data quality and alignment
- Key drivers supporting the forecast decision
```

**Synthesis Logic**:
- **High Confidence**: All three data sources align (e.g., strong financials + positive sentiment + favorable valuation)
- **Medium Confidence**: Mixed signals requiring balanced interpretation
- **Low Confidence**: Limited data availability or conflicting indicators

## Setup Instructions

### Prerequisites

- **Python 3.10+**
- **MySQL 8.0** (for request logging)
- **Git** (for cloning repository)

### 1. Clone Repository

```bash
git clone <repository-url>
cd ForecastingAgent
```

### 2. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

### 3. Database Setup (MySQL)

**Install MySQL** (if not already installed):

```bash
# macOS
brew install mysql
brew services start mysql

# Ubuntu/Linux
sudo apt update
sudo apt install mysql-server

# Windows
# Download from https://dev.mysql.com/downloads/mysql/
```

**Configure MySQL**:

```bash
# Secure installation
mysql_secure_installation

# Create database and set password
mysql -u root -p
```

**In MySQL prompt**:
```sql
CREATE DATABASE financial_forecasting;
FLUSH PRIVILEGES;
EXIT;
```

### 4. Environment Configuration

**Create `.env` file**:
```bash
cp .env.example .env
```

**Edit `.env` with your settings**:
```env
# Database Configuration (REQUIRED)
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password_here
MYSQL_DATABASE=financial_forecasting

# Optional: LLM API Keys (Ollama used by default)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
HUGGINGFACE_API_TOKEN=your_hf_token_here
```

### 5. LLM Provider Setup

The system supports multiple LLM providers with automatic fallback:

**Option 1: Ollama (Recommended - No API keys required)**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download model
ollama pull llama3.1:8b
```

**Option 2: Cloud Providers**
- Add your API keys to `.env` file
- System will automatically use the best available provider

### 6. Verify Installation

```bash
# Test the system components
python scripts/test_complete_system.py
```

Expected output: `🎉 ALL TESTS PASSED! System is fully operational.`

## How to Run

### Start the FastAPI Server

```bash
uvicorn app.main:app --reload
```

**Expected startup logs**:
```
INFO: ✅ Connected to MySQL database
INFO: Financial Forecasting Agent API started successfully
INFO: Uvicorn running on http://127.0.0.1:8000
```

### API Documentation

- **Interactive API Docs**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health
- **Database Stats**: http://127.0.0.1:8000/debug/database

### Generate Financial Forecast

**REST API Endpoint**:
```bash
curl -X POST 'http://127.0.0.1:8000/forecast' \
     -H 'Content-Type: application/json' \
     -d '{
       "company_symbol": "TCS",
       "forecast_period": "Q2-2025"
     }'
```

**Response Format**:
```json
{
  "company_symbol": "TCS",
  "forecast_period": "Q2-2025",
  "overall_outlook": "positive",
  "investment_recommendation": "buy",
  "analyst_confidence": 0.85,
  "current_price": 3135.8,
  "target_price": 3606.17,
  "target_upside_percent": 15.0,
  "market_cap_crores": 1234382.6,
  "pe_ratio": 23.0,
  "valuation_assessment": "fairly_valued",
  "management_sentiment": "positive",
  "management_optimism_score": 0.8,
  "key_drivers": [
    "employee costs trending downwards",
    "enterprises prioritizing targeted technology transformations", 
    "AI driving product innovation"
  ],
  "business_outlook_insights": [
    "TCS expects employee costs to trend downwards towards 45% range over next two-three quarters as growth picks up."
  ],
  "growth_opportunities": [
    "Enterprises are prioritizing targeted technology transformations to deliver operational efficiencies and cost savings.",
    "AI has established itself as a fundamental driver of product innovation across all sub-segments under TechSS."
  ],
  "processing_time": 52.46,
  "generated_at": "2025-07-26T14:21:54.523418",
  "data_sources": ["live_market_data", "earnings_transcripts", "financial_reports"],
  "success": true
}
```

### Verify Database Logging

**Check MySQL logs**:
```bash
mysql -u root -p
USE financial_forecasting;

SELECT id, company_symbol, 
       JSON_EXTRACT(response_data, '$.investment_recommendation') AS recommendation,
       JSON_EXTRACT(response_data, '$.analyst_confidence') AS confidence,
       processing_time, created_at 
FROM forecast_requests 
ORDER BY created_at DESC 
LIMIT 5;
```

## Supported Companies

The system works with any NSE-listed company. Examples:
- **TCS** (Tata Consultancy Services)
- **INFY** (Infosys)
- **RELIANCE** (Reliance Industries)
- **HDFCBANK** (HDFC Bank)

## Error Handling

### Common Issues

**1. MySQL Connection Failed**
```
ERROR: MySQL connection failed: Access denied for user 'root'@'localhost'
```
**Solution**: Verify MySQL password in `.env` file matches your actual MySQL root password.

**2. No LLM Provider Available**
```
ERROR: No LLM providers available
```
**Solution**: Install Ollama (`ollama pull llama3.1:8b`) or add API keys to `.env` file.

**3. Network/Data Issues**
```
WARNING: Failed to fetch market data for SYMBOL
```
**Solution**: Check internet connection. System will continue with available data sources.

### Graceful Degradation

The system is designed to work even with partial data:
- **No market data**: Uses financial and qualitative analysis only
- **No transcript data**: Focuses on financial metrics and market context  
- **No financial data**: Provides market-based analysis with qualitative insights

## Technical Stack

- **Backend**: FastAPI with async support
- **AI Framework**: LangChain for agent orchestration
- **Database**: MySQL 8.0 with SQLAlchemy ORM
- **Vector Store**: ChromaDB with sentence-transformers embeddings
- **Document Processing**: pdfplumber for PDF table extraction
- **Market Data**: Yahoo Finance API integration
- **LLM Support**: Ollama, OpenAI, Anthropic, Hugging Face

## Performance Metrics

- **Average Processing Time**: 45-60 seconds for complete analysis
- **Data Sources**: 3 (financial reports, earnings transcripts, live market data)
- **Analysis Depth**: 10+ financial metrics, 3-5 qualitative insights per company
- **Accuracy**: 85%+ confidence scores on successful extractions
- **Uptime**: Designed for 99.9% availability with graceful error handling

## Contributing

This is a take-home assignment project. For production deployment:

1. **Security**: Add authentication and rate limiting
2. **Scalability**: Implement Redis caching for market data
3. **Monitoring**: Add comprehensive logging and metrics
4. **Testing**: Expand test coverage for edge cases

## License

Private academic project - All rights reserved.