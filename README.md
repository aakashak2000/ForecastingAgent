# TCS Financial Forecasting Agent

An intelligent AI agent system that analyzes Tata Consultancy Services (TCS) financial documents and earnings transcripts to generate comprehensive business outlook forecasts. Built with FastAPI, LangChain, and multiple specialized AI tools for automated financial analysis.

## Project Overview

This system goes beyond traditional Q&A by autonomously discovering, analyzing, and synthesizing financial data from multiple sources to produce reasoned qualitative forecasts. The agent leverages specialized tools to extract quantitative metrics from quarterly reports and perform semantic analysis of earnings call transcripts.

### Key Capabilities

- **Automated Financial Data Extraction**: Processes quarterly financial reports to extract key metrics (revenue, profit, margins)
- **Qualitative Sentiment Analysis**: RAG-based analysis of earnings call transcripts for management outlook and themes
- **Multi-Source Synthesis**: Combines quantitative trends with qualitative insights for comprehensive forecasting
- **Structured Output Generation**: Produces machine-readable JSON forecasts with consistent schema
- **Comprehensive Logging**: Full request tracking and tool execution logging to MySQL database

## Architecture

### Agent-Based Design
The system employs a multi-tool agent architecture where specialized tools handle distinct aspects of financial analysis:

- **FinancialDataExtractorTool**: Extracts and processes numerical data from quarterly reports
- **QualitativeAnalysisTool**: Performs semantic search and analysis across earnings transcripts
- **MarketDataTool**: Integrates current market context and stock performance data

### LLM Provider Strategy
The system implements a fallback hierarchy to ensure maximum compatibility across different environments:

1. **Primary**: Ollama (local, no API keys required)
2. **Enhanced**: OpenAI GPT-4 (if API key available)
3. **Alternative**: Hugging Face Inference API (free tier)
4. **Enterprise**: Anthropic Claude (for production deployments)

## Technical Stack

- **Backend**: FastAPI with async support
- **AI Framework**: LangChain for agent orchestration
- **Database**: MySQL 8.0 with SQLAlchemy ORM
- **Vector Store**: ChromaDB for semantic search
- **Document Processing**: PyPDF2, BeautifulSoup for web scraping
- **LLM Options**: Ollama, OpenAI, Anthropic, Hugging Face

## Project Structure
