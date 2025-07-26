import logging
import time
from typing import Optional, Dict, List

from tools.financial_extractor import FinancialDataExtractorTool
from tools.qualitative_analyzer import QualitativeAnalysisTool
from tools.market_data import MarketDataTool
from models.forecast_result import ForecastResult
from app.llm_manager import LLMProviderManager

logger = logging.getLogger(__name__)

class FinancialForecastingAgent:
    """
    Master agent that orchestrates all three tools for comprehensive forecasts
    """
    
    def __init__(self):
        # Initialize all specialized tools
        self.financial_extractor = FinancialDataExtractorTool()
        self.qualitative_analyzer = QualitativeAnalysisTool()
        self.market_data_tool = MarketDataTool()
        self.llm_manager = LLMProviderManager()
        self.llm = None
        
        logger.info("FinancialForecastingAgent initialized with 3 tools")
    
    def generate_forecast(self, company_symbol: str, forecast_period: str = "Q2-2025") -> ForecastResult:
        """
        Generate comprehensive forecast using all three analysis tools
        
        Input: company_symbol="TCS", forecast_period="Q2-2025"
        Output: Complete ForecastResult with financial + qualitative + market analysis
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting comprehensive forecast generation for {company_symbol}")
            
            # Initialize LLM if needed
            if not self.llm:
                self.llm = self.llm_manager.get_llm()
            
            # Step 1: Download and extract fresh financial data
            logger.info("Step 1: Extracting financial metrics from quarterly reports...")
            financial_result = self._get_financial_data(company_symbol)
            
            # Step 2: Ensure RAG data exists and analyze transcripts
            logger.info("Step 2: Analyzing earnings call transcripts...")
            qualitative_result = self._get_qualitative_insights(company_symbol)
            
            # Step 3: Get live market data
            logger.info("Step 3: Fetching live market data...")
            market_data, market_context = self._get_market_data(company_symbol)
            
            # Step 4: Analyze multi-quarter trends
            logger.info("Step 4: Analyzing quarterly trends...")
            quarterly_trends = self._analyze_quarterly_trends(financial_result, company_symbol)
            
            # Step 5: Synthesize comprehensive forecast
            logger.info("Step 5: Synthesizing forecast with LLM...")
            synthesis = self._synthesize_comprehensive_forecast(
                financial_result, qualitative_result, market_data, market_context, quarterly_trends
            )
            
            # Step 6: Create complete forecast result
            processing_time = time.time() - start_time
            
            forecast_result = ForecastResult(
                company_symbol=company_symbol,
                forecast_period=forecast_period,
                
                # Store all tool results
                financial_metrics=financial_result.metrics if financial_result else None,
                qualitative_analysis=qualitative_result,
                market_data=market_data,
                market_context=market_context,
                
                # Synthesized forecast
                overall_outlook=synthesis["overall_outlook"],
                confidence_score=synthesis["confidence_score"],
                key_drivers=synthesis["key_drivers"],
                investment_recommendation=synthesis["investment_recommendation"],
                
                processing_time=processing_time
            )
            
            logger.info(f"Comprehensive forecast complete: {synthesis['overall_outlook']} outlook, {synthesis['confidence_score']:.2f} confidence")
            return forecast_result
            
        except Exception as e:
            logger.error(f"Forecast generation failed: {e}")
            return self._create_error_result(company_symbol, forecast_period, str(e), time.time() - start_time)
    
    def _get_financial_data(self, company_symbol: str):
        """Extract fresh financial metrics from quarterly reports"""
        try:
            logger.info("Downloading latest quarterly financial reports...")
            
            # Download fresh financial reports
            from utils.data_downloader import ScreenerDataDownloader
            downloader = ScreenerDataDownloader()
            results = downloader.get_latest_documents(company_symbol, max_reports=2, max_transcripts=0)
            
            if not results['annual_reports']:
                logger.warning(f"No financial reports found for {company_symbol}")
                return None
            
            # Extract from most recent report
            latest_report = results['annual_reports'][0]
            logger.info(f"Extracting from {latest_report['title']}")
            
            extraction_result = self.financial_extractor.extract_financial_data(
                pdf_path=latest_report['local_path'],
                company_symbol=company_symbol,
                report_period=f"FY{latest_report.get('year', 'Latest')}"
            )
            
            if extraction_result.success and extraction_result.metrics:
                metrics = extraction_result.metrics
                logger.info(f"✅ Financial extraction successful:")
                logger.info(f"   Revenue: ₹{metrics.total_revenue} Cr" if metrics.total_revenue else "   Revenue: Not extracted")
                logger.info(f"   Net Profit: ₹{metrics.net_profit} Cr" if metrics.net_profit else "   Net Profit: Not extracted")
                logger.info(f"   Operating Margin: {metrics.operating_margin}%" if metrics.operating_margin else "   Operating Margin: Not extracted")
                return extraction_result
            else:
                logger.warning("Financial extraction failed or returned no metrics")
                return None
                
        except Exception as e:
            logger.warning(f"Financial data extraction failed: {e}")
            return None
    
    def _get_qualitative_insights(self, company_symbol: str):
        """Get qualitative analysis with automatic transcript download"""
        try:
            logger.info("Ensuring transcript data availability...")
            
            # Check if we have transcript data
            stats = self.qualitative_analyzer.vectorstore.get_collection_stats()
            companies = stats.get('companies', [])
            
            if company_symbol not in companies:
                logger.info(f"Downloading transcript data for {company_symbol}...")
                success = self._download_company_transcripts(company_symbol)
                if not success:
                    logger.warning(f"Could not download transcript data for {company_symbol}")
                    return None
            
            # Run qualitative analysis
            qualitative_result = self.qualitative_analyzer.analyze_transcripts(
                company_symbol=company_symbol,
                analysis_period="Q1-2025"
            )
            
            if qualitative_result.success:
                logger.info(f"✅ Qualitative analysis successful:")
                logger.info(f"   Total insights: {qualitative_result.total_insights}")
                logger.info(f"   Management sentiment: {qualitative_result.management_sentiment.overall_tone}")
                logger.info(f"   Confidence: {qualitative_result.average_confidence:.2f}")
                return qualitative_result
            else:
                logger.warning("Qualitative analysis failed")
                return None
                
        except Exception as e:
            logger.warning(f"Qualitative analysis failed: {e}")
            return None
    
    def _download_company_transcripts(self, company_symbol: str) -> bool:
        """Download and add transcript data for a company on-demand"""
        try:
            from utils.data_downloader import ScreenerDataDownloader
            
            downloader = ScreenerDataDownloader()
            results = downloader.get_latest_documents(company_symbol, max_reports=0, max_transcripts=3)
            
            if not results['transcripts']:
                logger.warning(f"No transcripts found for {company_symbol}")
                return False
            
            # Add to vector store
            total_chunks = 0
            for transcript in results['transcripts']:
                content = transcript.get('full_content', transcript.get('content', ''))
                if len(content) > 2000:  # Require substantial content
                    chunks_added = self.qualitative_analyzer.vectorstore.add_transcript(
                        transcript_text=content,
                        company_symbol=company_symbol,
                        transcript_date=transcript['date'],
                        source_info={'source': 'earnings_call', 'auto_download': True}
                    )
                    total_chunks += chunks_added
                    logger.info(f"   Added {chunks_added} chunks from {transcript['date']}")
            
            if total_chunks > 0:
                logger.info(f"✅ Successfully added {total_chunks} transcript chunks for {company_symbol}")
                return True
            else:
                logger.warning(f"No usable transcript content for {company_symbol}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to download transcripts for {company_symbol}: {e}")
            return False
    
    def _get_market_data(self, company_symbol: str):
        """Get live market data and context"""
        try:
            logger.info("Fetching live market data...")
            
            market_data = self.market_data_tool.get_stock_data(company_symbol)
            if not market_data:
                logger.warning("Could not fetch market data")
                return None, None
            
            market_context = self.market_data_tool.analyze_market_context(market_data)
            
            logger.info(f"✅ Market data retrieved:")
            logger.info(f"   Current Price: ₹{market_data.current_price:,.2f}")
            logger.info(f"   P/E Ratio: {market_data.pe_ratio}")
            logger.info(f"   Valuation: {market_context.current_valuation if market_context else 'unknown'}")
            
            return market_data, market_context
            
        except Exception as e:
            logger.warning(f"Market data collection failed: {e}")
            return None, None
    
    def _analyze_quarterly_trends(self, financial_result, company_symbol: str) -> Dict:
        """Analyze quarterly trends for forecasting"""
        try:
            logger.info("Analyzing quarterly trends...")
            
            trends = {
                "revenue_trend": "stable",
                "margin_trend": "improving", 
                "growth_outlook": "positive",
                "forecast_metrics": {},
                "trend_confidence": 0.6
            }
            
            if financial_result and financial_result.metrics:
                metrics = financial_result.metrics
                
                # Basic trend analysis (can be enhanced with multiple quarters)
                if metrics.total_revenue:
                    # Estimate next quarter (simple growth assumption)
                    trends["forecast_metrics"]["revenue_estimate"] = metrics.total_revenue * 1.03  # 3% growth
                    trends["revenue_trend"] = "growing"
                
                if metrics.operating_margin:
                    if metrics.operating_margin > 20:
                        trends["margin_trend"] = "healthy"
                    trends["forecast_metrics"]["margin_estimate"] = metrics.operating_margin + 0.5  # Slight improvement
                
                trends["trend_confidence"] = 0.8
                logger.info(f"✅ Trend analysis: {trends['revenue_trend']} revenue, {trends['margin_trend']} margins")
            
            return trends
            
        except Exception as e:
            logger.warning(f"Quarterly trend analysis failed: {e}")
            return {"trend_confidence": 0.3}
    
    def _synthesize_comprehensive_forecast(self, financial_result, qualitative_result, 
                                         market_data, market_context, quarterly_trends):
        """Synthesize all data sources into comprehensive forecast using LLM"""
        try:
            # Build comprehensive analysis text
            analysis_summary = self._build_comprehensive_analysis(
                financial_result, qualitative_result, market_data, market_context, quarterly_trends
            )
            
            # Create comprehensive synthesis prompt
            prompt = f"""
You are a senior financial analyst creating a comprehensive quarterly forecast by integrating:

1. FINANCIAL METRICS (from quarterly reports)
2. MANAGEMENT INSIGHTS (from earnings call transcripts) 
3. MARKET CONTEXT (live stock data and valuation)
4. QUARTERLY TRENDS (growth patterns and forecasts)

COMPREHENSIVE ANALYSIS:
{analysis_summary}

TASK: Create a unified investment forecast for the next quarter.

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "overall_outlook": "<positive|neutral|negative>",
    "confidence_score": <0.0_to_1.0>,
    "investment_recommendation": "<buy|hold|sell>",
    "key_drivers": [
        "financial trend 1",
        "management insight 1", 
        "market factor 1"
    ],
    "forecast_rationale": "2-3 sentence explanation combining all data sources",
    "next_quarter_outlook": "specific predictions for upcoming quarter",
    "primary_risks": ["risk 1", "risk 2"],
    "primary_opportunities": ["opportunity 1", "opportunity 2"]
}}

GUIDELINES:
- Integrate insights from ALL data sources
- Higher confidence when all sources align
- Consider financial trends, management sentiment, and market positioning
- Focus on actionable investment thesis
"""
            
            llm_response = self.llm.invoke(prompt)
            synthesis = self._parse_comprehensive_synthesis(llm_response)
            
            logger.info(f"✅ Comprehensive synthesis: {synthesis['overall_outlook']} outlook")
            return synthesis
            
        except Exception as e:
            logger.error(f"Forecast synthesis failed: {e}")
            return self._get_fallback_synthesis()
    
    def _build_comprehensive_analysis(self, financial_result, qualitative_result, 
                                    market_data, market_context, quarterly_trends):
        """Build detailed analysis summary for LLM"""
        sections = []
        
        # Financial Analysis Section
        sections.append("=== FINANCIAL METRICS ANALYSIS ===")
        if financial_result and financial_result.metrics:
            metrics = financial_result.metrics
            sections.append(f"Revenue: ₹{metrics.total_revenue} Crores" if metrics.total_revenue else "Revenue: Not available")
            sections.append(f"Net Profit: ₹{metrics.net_profit} Crores" if metrics.net_profit else "Net Profit: Not available")
            sections.append(f"Operating Margin: {metrics.operating_margin}%" if metrics.operating_margin else "Operating Margin: Not available")
            sections.append(f"Extraction Confidence: {metrics.extraction_confidence:.1f}")
        else:
            sections.append("Financial metrics: Not available")
        
        # Qualitative Analysis Section
        sections.append("\n=== MANAGEMENT INSIGHTS (from earnings calls) ===")
        if qualitative_result and qualitative_result.success:
            sentiment = qualitative_result.management_sentiment
            sections.append(f"Management Sentiment: {sentiment.overall_tone} (optimism: {sentiment.optimism_score:.1f})")
            
            if qualitative_result.business_outlook:
                sections.append("Business Outlook Insights:")
                for insight in qualitative_result.business_outlook[:3]:
                    sections.append(f"  - {insight.insight}")
            
            if qualitative_result.growth_opportunities:
                sections.append("Growth Opportunities:")
                for opp in qualitative_result.growth_opportunities[:2]:
                    sections.append(f"  - {opp.insight}")
        else:
            sections.append("Management insights: Not available")
        
        # Market Analysis Section
        sections.append("\n=== LIVE MARKET CONTEXT ===")
        if market_data and market_context:
            sections.append(f"Current Price: ₹{market_data.current_price:,.2f}")
            sections.append(f"Price Performance: {market_data.price_change_percent:+.1f}%")
            sections.append(f"Valuation: {market_context.current_valuation}")
            sections.append(f"Market Risk Level: {market_context.risk_level}")
            sections.append(f"P/E Ratio: {market_data.pe_ratio:.1f}")
        else:
            sections.append("Market data: Not available")
        
        # Quarterly Trends Section
        sections.append("\n=== QUARTERLY TRENDS & FORECASTS ===")
        sections.append(f"Revenue Trend: {quarterly_trends.get('revenue_trend', 'unknown')}")
        sections.append(f"Margin Trend: {quarterly_trends.get('margin_trend', 'unknown')}")
        sections.append(f"Growth Outlook: {quarterly_trends.get('growth_outlook', 'unknown')}")
        if quarterly_trends.get('forecast_metrics'):
            forecasts = quarterly_trends['forecast_metrics']
            if 'revenue_estimate' in forecasts:
                sections.append(f"Next Quarter Revenue Estimate: ₹{forecasts['revenue_estimate']:.0f} Cr")
        
        return '\n'.join(sections)
    
    def _parse_comprehensive_synthesis(self, llm_response: str):
        """Parse LLM comprehensive synthesis response"""
        import json
        import re
        
        try:
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                return {
                    "overall_outlook": parsed.get("overall_outlook", "neutral"),
                    "confidence_score": float(parsed.get("confidence_score", 0.6)),
                    "investment_recommendation": parsed.get("investment_recommendation", "hold"),
                    "key_drivers": parsed.get("key_drivers", ["Analysis completed"]),
                    "forecast_rationale": parsed.get("forecast_rationale", ""),
                    "next_quarter_outlook": parsed.get("next_quarter_outlook", ""),
                    "primary_risks": parsed.get("primary_risks", []),
                    "primary_opportunities": parsed.get("primary_opportunities", [])
                }
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse comprehensive synthesis: {e}")
        
        return self._get_fallback_synthesis()
    
    def _get_fallback_synthesis(self):
        """Fallback synthesis when LLM parsing fails"""
        return {
            "overall_outlook": "neutral",
            "confidence_score": 0.5,
            "investment_recommendation": "hold",
            "key_drivers": ["Limited data analysis"],
            "forecast_rationale": "Analysis based on available data sources",
            "next_quarter_outlook": "Monitoring required",
            "primary_risks": ["Market volatility"],
            "primary_opportunities": ["Business fundamentals"]
        }
    
    def _create_error_result(self, company_symbol: str, forecast_period: str, 
                           error_message: str, processing_time: float) -> ForecastResult:
        """Create error result when forecast fails"""
        return ForecastResult(
            company_symbol=company_symbol,
            forecast_period=forecast_period,
            overall_outlook="neutral",
            confidence_score=0.0,
            investment_recommendation="hold",
            key_drivers=["Analysis failed"],
            success=False,
            error_message=error_message,
            processing_time=processing_time
        )