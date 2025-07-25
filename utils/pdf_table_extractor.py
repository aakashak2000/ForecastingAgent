import logging
import pdfplumber
from typing import List, Dict, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFTableExtractor:
    """
    Extracts financial tables from PDF reports using pdfplumber
    """
    
    def __init__(self):
        self.financial_keywords = [
            'revenue', 'profit', 'income', 'expense', 'margin', 
            'ebitda', 'operating', 'net', 'total', 'gross',
            'turnover', 'sales', 'earnings'
        ]
        logging.getLogger('pdfminer.pdfinterp').setLevel(logging.ERROR)
        logging.getLogger('pdfminer.converter').setLevel(logging.ERROR) 
        logging.getLogger('pdfminer.pdfpage').setLevel(logging.ERROR)
    
    def extract_tables_from_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Extract all tables from PDF that look financial
        
        Input: PDF file path
        Output: List of table dictionaries with metadata
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        tables_found = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                logger.info(f"Processing PDF: {pdf_path.name} ({len(pdf.pages)} pages)")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_tables = self._extract_page_tables(page, page_num)
                    tables_found.extend(page_tables)
                    
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            raise
        
        # Filter and rank tables by financial relevance
        financial_tables = self._filter_financial_tables(tables_found)
        
        logger.info(f"Found {len(financial_tables)} financial tables out of {len(tables_found)} total")
        return financial_tables
    
    def _extract_page_tables(self, page, page_num: int) -> List[Dict]:
        """Extract all tables from a single page"""
        page_tables = []
        
        try:
            tables = page.extract_tables()
            
            for table_idx, table in enumerate(tables):
                if self._is_valid_table(table):
                    table_dict = {
                        'page_number': page_num,
                        'table_index': table_idx,
                        'raw_table': table,
                        'table_text': self._table_to_text(table),
                        'row_count': len(table),
                        'col_count': len(table[0]) if table else 0
                    }
                    page_tables.append(table_dict)
                    
        except Exception as e:
            logger.warning(f"Page {page_num} table extraction failed: {e}")
        
        return page_tables
    
    def _is_valid_table(self, table: List[List]) -> bool:
        """Check if table has minimum structure for financial data"""
        if not table or len(table) < 2:
            return False
        
        # Must have at least 2 columns and 2 rows
        if not table[0] or len(table[0]) < 2:
            return False
        
        # Check for mostly empty table
        non_empty_cells = sum(1 for row in table for cell in row if cell and str(cell).strip())
        total_cells = len(table) * len(table[0])
        
        return non_empty_cells > (total_cells * 0.3)  # At least 30% filled
    
    def _table_to_text(self, table: List[List]) -> str:
        """Convert table to readable text format"""
        if not table:
            return ""
        
        text_lines = []
        for row in table:
            # Clean and join cells
            clean_cells = [str(cell or '').strip() for cell in row]
            text_lines.append(' | '.join(clean_cells))
        
        return '\n'.join(text_lines)
    
    def _filter_financial_tables(self, all_tables: List[Dict]) -> List[Dict]:
        """Filter tables that likely contain financial data"""
        financial_tables = []
        
        for table in all_tables:
            table_text = table['table_text'].lower()
            
            # Score table based on financial keywords
            score = sum(1 for keyword in self.financial_keywords 
                       if keyword in table_text)
            
            # Add score and filter
            table['financial_score'] = score
            
            if score >= 2:  # Must contain at least 2 financial keywords
                financial_tables.append(table)
        
        # Sort by financial relevance (highest score first)
        financial_tables.sort(key=lambda x: x['financial_score'], reverse=True)
        
        return financial_tables
