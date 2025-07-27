# System Architecture

## Overview

The Financial Forecasting Agent employs a multi-tool agent architecture where specialized tools handle distinct aspects of financial analysis. The system is designed for modularity, reliability, and scalability.

## System Components

### Core Architecture

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

### Data Processing Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Source    │    │  Processing │    │  Analysis   │    │   Output    │
│   Data      │    │   Layer     │    │   Layer     │    │   Layer     │
├─────────────┤    ├─────────────┤    ├─────────────┤    ├─────────────┤
│• PDF Reports│───▶│• Table Extr.│───▶│• LLM Parse  │───▶│• Metrics    │
│• Transcripts│───▶│• Text Chunk │───▶│• Vector DB  │───▶│• Insights   │
│• Live Data  │───▶│• API Fetch  │───▶│• Valuation  │───▶│• Context    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                 │
                                                                 ▼
                                                    ┌─────────────────┐
                                                    │ Master Synthesis│
                                                    │ & Forecast Gen. │
                                                    └─────────────────┘
```

## Component Deep Dive

### 1. FastAPI Application Layer

**Purpose**: HTTP API interface with async request handling

**Components**:
- `app/main.py`: Application bootstrap and lifespan management
- `app/api/routes.py`: REST endpoint definitions and request handling
- `app/database.py`: Database connection and logging management

**Key Features**:
- Async request processing for better performance
- Global agent initialization for faster responses
- Comprehensive error handling and graceful degradation
- Automatic database fallback (MySQL → SQLite)

### 2. Agent Orchestrator

**Purpose**: Master coordinator that manages tool execution and synthesis

**Architecture**:
```python
class FinancialForecastingAgent:
    def __init__(self):
        self.financial_extractor = FinancialDataExtractorTool()
        self.qualitative_analyzer = QualitativeAnalysisTool()
        self.market_data_tool = MarketDataTool()
        self.llm_manager = LLMProviderManager()
    
    def generate_forecast(self, company_symbol, forecast_period):
        # 1. Financial data extraction
        # 2. Qualitative analysis
        # 3. Market data gathering
        # 4. Multi-source synthesis
        # 5. Structured output generation
```

**Reasoning Flow**:
1. **Parallel Data Gathering**: Tools can operate independently
2. **Sequential Analysis**: Each tool builds on available data
3. **Synthesis Phase**: LLM combines all insights
4. **Confidence Scoring**: Based on data quality and alignment

### 3. Financial Data Extraction Tool

**Architecture**:
```
PDF Input → Table Detection → Content Extraction → LLM Parsing → Structured Output
```

**Components**:
- `utils/data_downloader.py`: PDF acquisition from public sources
- `utils/pdf_table_extractor.py`: Table detection and extraction using pdfplumber
- `tools/financial_extractor.py`: LLM-based parsing and validation

**Processing Pipeline**:
1. **Document Discovery**: Scrapes screener.in for latest reports
2. **PDF Download**: Caches documents locally for processing
3. **Table Extraction**: Identifies financial tables using keyword matching
4. **LLM Parsing**: Extracts structured metrics with confidence scoring
5. **Validation**: Business logic checks for data consistency

### 4. Qualitative Analysis Tool (RAG)

**Architecture**:
```
Transcript Input → Chunking → Embedding → Vector Storage → Semantic Search → LLM Analysis
```

**Components**:
- `vector_store/transcript_vectorstore.py`: ChromaDB-based vector storage
- `tools/qualitative_analyzer.py`: Semantic search and analysis
- `models/qualitative_insights.py`: Structured output models

**RAG Pipeline**:
1. **Intelligent Chunking**: Segments by speaker and topic
2. **Embedding Generation**: sentence-transformers for semantic understanding
3. **Vector Storage**: ChromaDB with persistent storage
4. **Multi-Query Search**: Separate searches for outlook, risks, opportunities
5. **LLM Synthesis**: Combines retrieved chunks into structured insights

**Search Strategy**:
```python
# Multiple specialized searches
outlook_chunks = search("management outlook future guidance")
risk_chunks = search("risk factors challenges headwinds")
opportunity_chunks = search("growth opportunities investments")

# Quality-based filtering
high_quality = filter(chunks, min_similarity=0.3, min_quality=0.5)
```

### 5. Market Data Tool

**Architecture**:
```
Yahoo Finance API → Data Fetch → Validation → Analysis → Context Generation
```

**Components**:
- `tools/market_data.py`: API integration and analysis logic
- `models/market_data.py`: Structured data models

**Analysis Logic**:
```python
def analyze_market_context(self, market_data):
    # Valuation assessment
    valuation = self._assess_valuation(market_data.pe_ratio)
    
    # Momentum analysis
    momentum = self._analyze_momentum(market_data.price_change_percent)
    
    # Risk evaluation
    risk = self._evaluate_risk(market_data, price_range_position)
    
    return MarketContext(valuation, momentum, risk, insights)
```

### 6. LLM Provider Management

**Architecture**:
```
Request → Provider Selection → Fallback Chain → Response Validation
```

**Fallback Strategy**:
```python
providers = [
    ("ollama", self._try_ollama),      # Local, free
    ("openai", self._try_openai),      # Premium, fast  
    ("anthropic", self._try_anthropic), # Premium, advanced
    ("huggingface", self._try_hf),     # Free tier
]

# Automatic fallback on failure
for name, provider_func in providers:
    try:
        return provider_func()
    except Exception:
        continue  # Try next provider
```

## Data Flow Patterns

### 1. Request Processing Flow

```
HTTP Request → Route Handler → Agent Orchestrator → Tool Execution → LLM Synthesis → JSON Response
```

### 2. Error Handling Flow

```
Tool Failure → Graceful Degradation → Partial Analysis → Lower Confidence Score → Continued Processing
```

### 3. Caching Strategy

```
Fresh Request → Check Cache → Download if Needed → Process → Cache Results → Return Data
```

## Performance Optimizations

### 1. Startup Optimization

- **Global Agent Instance**: Initialized once at startup, not per request
- **Model Preloading**: Sentence transformers loaded during app startup
- **Connection Pooling**: Database connections managed efficiently

### 2. Request Optimization

- **Parallel Processing**: Tools can operate independently where possible
- **Intelligent Caching**: Recent documents cached to avoid re-download
- **Streaming Responses**: Large responses can be streamed

### 3. Resource Management

- **Memory Efficiency**: PDF processing uses streaming where possible
- **Database Optimization**: Indexes on frequently queried columns
- **Vector Store Efficiency**: Optimized embeddings and search parameters

## Scalability Considerations

### Horizontal Scaling

- **Stateless Design**: All state managed in database or external storage
- **Load Balancer Ready**: Multiple instances can run behind load balancer
- **Database Scaling**: MySQL supports read replicas and clustering

### Vertical Scaling

- **CPU Optimization**: LLM processing can utilize multiple cores
- **Memory Scaling**: Vector stores can handle larger document collections
- **Storage Scaling**: Supports large PDF collections and vector databases

### Cloud Deployment

- **Container Ready**: Designed for Docker deployment
- **Cloud Database**: Supports cloud MySQL services (RDS, Cloud SQL)
- **API Scaling**: FastAPI supports async for high concurrency

## Security Architecture

### Data Protection

- **No Persistent Storage**: Raw financial data not stored permanently
- **Encrypted Transport**: HTTPS for all external communications
- **Database Security**: Parameterized queries prevent SQL injection

### Access Control

- **API Authentication**: Ready for JWT token integration
- **Rate Limiting**: Built-in throttling for external APIs
- **Input Validation**: All inputs validated before processing

### Privacy

- **Local Processing**: Financial analysis done locally
- **Minimal Data Retention**: Only aggregated results stored
- **Audit Trail**: All requests logged for compliance

## Monitoring and Observability

### Logging Strategy

- **Structured Logging**: JSON-formatted logs for easy parsing
- **Request Tracing**: Full request lifecycle tracking
- **Performance Metrics**: Processing times and success rates

### Health Monitoring

- **Component Health Checks**: Individual tool status monitoring
- **Database Health**: Connection and performance monitoring
- **External API Health**: Market data service monitoring

### Metrics Collection

- **Request Metrics**: Volume, latency, success rates
- **Business Metrics**: Forecast accuracy, confidence distributions
- **System Metrics**: Resource utilization, error rates