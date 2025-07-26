#!/usr/bin/env python3

import logging
import sys
import os
import json
import glob
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_pdf_extractor():
    """Test PDF table extraction with real TCS annual report"""
    
    print("🧪 Testing PDF Table Extractor with TCS Annual Report")
    print("=" * 60)
    
    try:
        from utils.pdf_table_extractor import PDFTableExtractor
        
        # Look for TCS PDF in common temp locations
        search_patterns = [
            "/var/folders/*/T/*TCS*.pdf",
            "/tmp/*TCS*.pdf", 
            "temp_downloads/*TCS*.pdf"
        ]
        
        pdf_path = None
        for pattern in search_patterns:
            files = glob.glob(pattern)
            if files:
                pdf_path = files[0]  # Use most recent
                break
        
        if not pdf_path:
            print("❌ No TCS PDF found")
            print("   Searched in: /var/folders/.../T/, /tmp/, temp_downloads/")
            print("   Run test_data_downloader.py first to download PDF")
            return False
        
        print(f"📄 Using PDF: {Path(pdf_path).name}")
        print(f"   Full path: {pdf_path}")
        print(f"   File size: {os.path.getsize(pdf_path)/1024:.1f} KB")
        
        # Initialize extractor
        extractor = PDFTableExtractor()
        print("✅ PDFTableExtractor initialized")
        
        # Extract tables
        print(f"\n🔍 Extracting tables from PDF...")
        tables = extractor.extract_tables_from_pdf(pdf_path)
        
        print(f"\n📊 Extraction Results:")
        print(f"   Total financial tables found: {len(tables)}")
        
        if not tables:
            print("⚠️  No financial tables detected")
            return False
        
        # Show top 3 most relevant tables
        print(f"\n🏆 Top Financial Tables (by relevance score):")
        
        for i, table in enumerate(tables[:3]):
            print(f"\n   Table #{i+1}:")
            print(f"     Page: {table['page_number']}")
            print(f"     Dimensions: {table['row_count']} rows × {table['col_count']} cols")
            print(f"     Financial Score: {table['financial_score']}/10")
            
            # Show first few lines of table content
            table_lines = table['table_text'].split('\n')
            preview_lines = table_lines[:4]  # First 4 rows
            
            print(f"     Content Preview:")
            for line in preview_lines:
                print(f"       {line[:80]}...")  # First 80 chars
            
            if len(table_lines) > 4:
                print(f"       ... ({len(table_lines)-4} more rows)")
        
        # Save detailed results for inspection
        output_file = "test_pdf_extraction_results.json"
        
        # Create clean results (limit table text for readability)
        clean_results = []
        for table in tables:
            clean_table = table.copy()
            clean_table['table_text_preview'] = table['table_text'][:500] + "..."
            clean_table.pop('raw_table', None)  # Remove raw table data
            clean_results.append(clean_table)
        
        with open(output_file, 'w') as f:
            json.dump(clean_results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {output_file}")
        print(f"🎉 PDF Table Extraction Test Complete!")
        
        return len(tables) > 0
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure pdfplumber is installed: pip install pdfplumber")
        return False
        
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_extractor()
    sys.exit(0 if success else 1)
