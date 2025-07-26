import json
from models.financial_metrics import FinancialMetrics, FinancialExtractionResult

# Test the models work
metrics = FinancialMetrics(
    company_symbol="TCS",
    report_period="FY2025",
    total_revenue=25826.0,
    net_profit=4467.0,
    extraction_confidence=0.9
)

print("✅ FinancialMetrics created:")
print(json.dumps(metrics.model_dump(), indent=2))

result = FinancialExtractionResult(
    success=True,
    metrics=metrics,
    source_file="TCS_FY2025.pdf",
    processing_time=2.34
)

print("\n✅ FinancialExtractionResult created:")
print(json.dumps(result.model_dump(), indent=2))
