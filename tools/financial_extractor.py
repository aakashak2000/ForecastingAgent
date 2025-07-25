import logging
import time
from typing import Optional, List
from pathlib import Path

from models.financial_metrics import FinancialMetrics, FinancialExtractionResult
from utils.pdf_table_extractor import PDFTableExtractor
from app.llm_manager import LLMProviderManager

logger = logging.getLogger(__name__)

class FinancialDataExtractorTool:
    """
    Extracts structured financial metrics from PDF reports using LLM parsing
    """
    
    def __init__(self):
        self.pdf_extractor = PDFTableExtractor()
        self.llm_manager = LLMProviderManager()
        self.llm = None
    
    def extract_financial_data(self, pdf_path: str, company_symbol: str, 
                             report_period: str = None) -> FinancialExtractionResult:
        """
        Main extraction method - processes PDF and returns structured financial data
        
        Input: PDF file path, company symbol, optional report period
        Output: FinancialExtractionResult with structured metrics
        """
        start_time = time.time()
        
        try:
            # Initialize LLM if needed
            if not self.llm:
                self.llm = self.llm_manager.get_llm()
                logger.info(f"Using LLM provider: {self.llm_manager.current_provider}")
            
            # Step 1: Extract tables from PDF
            logger.info(f"Extracting tables from {Path(pdf_path).name}")
            tables = self.pdf_extractor.extract_tables_from_pdf(pdf_path)
            
            if not tables:
                return FinancialExtractionResult(
                    success=False,
                    error_message="No financial tables found in PDF",
                    processing_time=time.time() - start_time,
                    source_file=pdf_path
                )
            
            # Step 2: Parse tables with LLM to extract metrics
            logger.info(f"Parsing {len(tables)} tables with LLM")
            metrics = self._parse_tables_with_llm(tables, company_symbol, report_period)
            
            processing_time = time.time() - start_time
            logger.info(f"Extraction completed in {processing_time:.2f}s")
            
            return FinancialExtractionResult(
                success=True,
                metrics=metrics,
                processing_time=processing_time,
                source_file=pdf_path
            )
            
        except Exception as e:
            logger.error(f"Financial extraction failed: {e}")
            return FinancialExtractionResult(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time,
                source_file=pdf_path
            )
    
    def _parse_tables_with_llm(self, tables: List[dict], company_symbol: str, 
                              report_period: str = None) -> FinancialMetrics:
        """
        Use LLM to parse table text and extract structured financial metrics
        """
        # Combine top 3 most relevant tables for LLM analysis
        top_tables = tables[:3]
        combined_table_text = self._combine_table_texts(top_tables)
        
        # Create LLM prompt for financial data extraction
        prompt = self._create_extraction_prompt(combined_table_text, company_symbol, report_period)
        
        # Get LLM response
        logger.debug("Sending extraction prompt to LLM")
        llm_response = self.llm.invoke(prompt)
        
        # DEBUG: Log the raw LLM response to see what went wrong
        logger.info("=== RAW LLM RESPONSE DEBUG ===")
        logger.info(f"LLM Response Length: {len(llm_response)}")
        logger.info(f"LLM Response Content:\n{llm_response}")
        logger.info("=== END DEBUG ===")
        
        # Parse LLM response into structured metrics
        metrics = self._parse_llm_response(llm_response, company_symbol, report_period, combined_table_text)
        
        return metrics
    
    def _combine_table_texts(self, tables: List[dict]) -> str:
        """Combine multiple table texts for LLM analysis"""
        combined = []
        
        for i, table in enumerate(tables):
            table_header = f"\n--- TABLE {i+1} (Page {table['page_number']}, Score: {table['financial_score']}) ---"
            combined.append(table_header)
            combined.append(table['table_text'])
        
        return '\n'.join(combined)
    
    def _create_extraction_prompt(self, table_text: str, company_symbol: str, 
                                 report_period: str = None) -> str:
        """Create structured prompt for LLM financial data extraction"""
        
        period_hint = f" for {report_period}" if report_period else ""
        
        prompt = f"""
You are a financial analyst extracting key metrics from {company_symbol} financial tables{period_hint}.

FINANCIAL TABLES:
{table_text}

TASK: Extract the following key financial metrics (values should be in Crores INR):

1. TOTAL REVENUE / TOTAL INCOME
2. NET PROFIT / NET PROFIT AFTER TAX  
3. OPERATING PROFIT / EBIT
4. OPERATING MARGIN (as percentage)
5. NET MARGIN (as percentage)

RULES:
- Look for the most recent/current year figures
- Values should be numerical only (remove commas, currency symbols)
- Margins should be percentages (0-100 range)
- If a metric is not found, use "null"
- Be confident in your extraction

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "total_revenue": <number_or_null>,
    "net_profit": <number_or_null>, 
    "operating_profit": <number_or_null>,
    "operating_margin": <number_or_null>,
    "net_margin": <number_or_null>,
    "confidence": <0.0_to_1.0>,
    "notes": "<brief_explanation_of_what_you_found>"
}}
"""
        
        return prompt.strip()
    
    def _parse_llm_response(self, llm_response: str, company_symbol: str, 
                           report_period: str = None, raw_source: str = None) -> FinancialMetrics:
        """
        Parse LLM JSON response into structured FinancialMetrics object
        """
        import json
        import re
        
        try:
            # Try to extract JSON from LLM response (sometimes has extra text)
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
            else:
                json_str = llm_response.strip()
            
            # FIX: Remove comma separators from numbers before parsing JSON
            # Pattern: find numbers with commas like "48,797"
            json_str = re.sub(r':\s*(\d{1,3}(?:,\d{3})+)', lambda m: ': ' + m.group(1).replace(',', ''), json_str)
            
            # Parse JSON response
            parsed_data = json.loads(json_str)
            logger.info(f"LLM extracted metrics: {parsed_data}")
            
            # Convert to FinancialMetrics object
            metrics = FinancialMetrics(
                company_symbol=company_symbol,
                report_period=report_period or "Unknown",
                total_revenue=self._safe_float(parsed_data.get('total_revenue')),
                net_profit=self._safe_float(parsed_data.get('net_profit')),
                operating_profit=self._safe_float(parsed_data.get('operating_profit')),
                operating_margin=self._safe_float(parsed_data.get('operating_margin')),
                net_margin=self._safe_float(parsed_data.get('net_margin')),
                extraction_confidence=self._safe_float(parsed_data.get('confidence', 0.5)),
                raw_source=raw_source[:1000] if raw_source else None  # Limit length
            )
            
            # Log successful extraction
            logger.info(f"Successfully created FinancialMetrics: Revenue={metrics.total_revenue}, "
                       f"Profit={metrics.net_profit}, Confidence={metrics.extraction_confidence}")
            
            return metrics
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.debug(f"Raw LLM response: {llm_response}")
            
            # Return fallback metrics with low confidence
            return self._create_fallback_metrics(company_symbol, report_period, raw_source)
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return self._create_fallback_metrics(company_symbol, report_period, raw_source)
    
    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float, handling None and invalid values"""
        if value is None or value == "null":
            return None
        
        try:
            # Handle string numbers with commas
            if isinstance(value, str):
                cleaned = value.replace(',', '').replace('₹', '').strip()
                if cleaned.lower() in ['null', 'none', '']:
                    return None
                return float(cleaned)
            
            return float(value)
            
        except (ValueError, TypeError):
            logger.warning(f"Could not convert to float: {value}")
            return None
    
    def _create_fallback_metrics(self, company_symbol: str, 
                                report_period: str = None, 
                                raw_source: str = None) -> FinancialMetrics:
        """Create fallback metrics when LLM parsing fails"""
        return FinancialMetrics(
            company_symbol=company_symbol,
            report_period=report_period or "Unknown",
            extraction_confidence=0.1,  # Very low confidence
            raw_source=raw_source[:500] if raw_source else "LLM parsing failed"
        )