import logging
import requests
from typing import Optional
from dataclasses import dataclass
from langchain_core.tools import BaseTool
from pydantic import Field

logger = logging.getLogger(__name__)

@dataclass
class FinancialMetrics:
    quarter: str
    year: str
    total_revenue = None
    net_profit = None
    operating_margin = None
    profit_margin = None
    revenue_growth_yoy = None

    def to_dict(self):
        return {
            "quarter": self.quarter,
            "year": self.year,
            "total_revenue": self.total_revenue,
            "net_profit": self.net_profit,
            "operating_margin": self.operating_margin,
            "profit_margin": self.profit_margin,
            "revenue_growth_yoy": self.revenue_growth_yoy,   
        }
    

class FinancialDataExtractorTool(BaseTool):
    """
    As a part of the requirements, this tool extracts financial metrics from quarterly reports.
    """
    name: str = "financial_data_extractor"
    description: str = "Downloads and extracts key financial metrics from quarterly reports"
    llm: Optional[object] = Field(default=None)

    def __init__(self, llm, **kwargs):
        super().__init__(llm=llm, **kwargs)