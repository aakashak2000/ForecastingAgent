import os
import re
import uuid
import hashlib
import logging
import tempfile
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ScreenerDataDownloader:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.download_cache = set()
        self.base_url = "https://www.screener.in"

    def get_company_documents(self, company_symbol: str) -> Dict[str, List[Dict]]:
        url = f"{self.base_url}/company/{company_symbol}/consolidated/#documents"
        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            return {
                "annual_reports": self._extract_annual_reports(soup),
                "concalls": self._extract_concalls(soup)
            }
        except Exception as e:
            logger.error(f"Failed to fetch documents for {company_symbol}: {e}")
            return {"annual_reports": [], "concalls": []}

    def _extract_annual_reports(self, soup: BeautifulSoup) -> List[Dict]:
        reports = []
        try:
            annual_header = soup.find('h3', string='Annual reports')
            if not annual_header:
                return reports
            
            reports_container = annual_header.find_next('ul', class_='list-links')
            if not reports_container:
                return reports
            
            for li in reports_container.find_all('li'):
                report_link = li.find('a', class_=lambda x: x and 'Annual+Report' in x)
                if report_link and report_link.get('href'):
                    link_text = report_link.get_text(strip=True)
                    href = report_link['href']
                    
                    year = None
                    if 'Financial Year' in link_text:
                        try:
                            year = int(link_text.split()[-1])
                        except (ValueError, IndexError):
                            pass
                    
                    if not year:
                        year_match = re.search(r'20\d{2}', link_text + href)
                        if year_match:
                            year = int(year_match.group())
                    
                    reports.append({
                        'year': year or 0,
                        'title': link_text or f'Annual Report {year}',
                        'pdf_url': href,
                        'source': 'annual_report'
                    })
            
            reports.sort(key=lambda x: x['year'], reverse=True)
            logger.info(f"Found {len(reports)} annual reports")
            
        except Exception as e:
            logger.error(f"Error extracting annual reports: {e}")
        
        return reports

    def _extract_concalls(self, soup: BeautifulSoup) -> List[Dict]:
        concalls = []
        try:
            concall_items = soup.find_all('li', class_='flex flex-gap-8 flex-wrap')
            
            for item in concall_items:
                full_text = item.get_text(strip=True)
                date_match = re.match(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})', full_text)
                
                if not date_match:
                    continue
                
                date_str = f"{date_match.group(1)} {date_match.group(2)}"
                
                transcript_link = item.find('a', string='Transcript')
                notes_link = item.find('a', string='Notes')
                
                concalls.append({
                    'date': date_str,
                    'transcript_url': transcript_link['href'] if transcript_link else None,
                    'notes_url': notes_link['href'] if notes_link else None,
                    'source': 'concall'
                })
                
            logger.info(f"Found {len(concalls)} concall entries")
            
        except Exception as e:
            logger.error(f"Error extracting concalls: {e}")
        
        return concalls

    def download_pdf_temp(self, url: str, description: str = "") -> Optional[str]:
        try:
            url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
            if url_hash in self.download_cache:
                return None
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            #temp_dir = tempfile.gettempdir()
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            temp_dir = os.path.join(project_root, "temp_downloads")
            os.makedirs(temp_dir, exist_ok=True) 
            safe_description = "".join(c for c in description if c.isalnum() or c in "._- ")[:30]
            filename = f"{safe_description}_{uuid.uuid4().hex[:8]}.pdf"
            file_path = os.path.join(temp_dir, filename)
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            self.download_cache.add(url_hash)
            logger.info(f"PDF downloaded: {file_path} ({len(response.content)/1024:.1f}KB)")
            
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to download PDF from {url}: {e}")
            return None

    def extract_transcript_content(self, transcript_url: str) -> Optional[str]:
        try:
            url_hash = hashlib.sha256(transcript_url.encode()).hexdigest()[:16]
            if url_hash in self.download_cache:
                return None
            
            response = self.session.get(transcript_url, timeout=20)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            
            if 'pdf' in content_type:
                return self._extract_pdf_text(response.content)
            else:
                return self._extract_html_text(response.content)
                
        except Exception as e:
            logger.error(f"Failed to extract transcript from {transcript_url}: {e}")
            return None

    def _extract_pdf_text(self, pdf_content: bytes) -> Optional[str]:
        try:
            import pdfplumber
            
            #temp_dir = tempfile.gettempdir()
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            temp_dir = os.path.join(project_root, "temp_downloads")
            os.makedirs(temp_dir, exist_ok=True) 
            temp_pdf = os.path.join(temp_dir, f"transcript_{uuid.uuid4().hex[:8]}.pdf")
            
            with open(temp_pdf, 'wb') as f:
                f.write(pdf_content)
            
            transcript_text = ""
            with pdfplumber.open(temp_pdf) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        transcript_text += page_text + "\n"
            
            os.remove(temp_pdf)
            
            if len(transcript_text) < 500:
                return None
            
            logger.info(f"PDF transcript extracted: {len(transcript_text)} characters")
            return transcript_text
            
        except ImportError:
            logger.error("pdfplumber not installed")
            return None
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return None

    def _extract_html_text(self, html_content: bytes) -> Optional[str]:
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            selectors = ['div.transcript-content', 'div.content', 'main', 'article']
            
            for selector in selectors:
                container = soup.select_one(selector)
                if container:
                    text = container.get_text(separator="\n", strip=True)
                    if len(text) > 500:
                        logger.info(f"HTML transcript extracted: {len(text)} characters")
                        return text
            
            return None
            
        except Exception as e:
            logger.error(f"HTML extraction failed: {e}")
            return None

    def get_latest_documents(self, company_symbol: str, max_reports: int = 2, max_transcripts: int = 3) -> Dict:
        logger.info(f"Fetching latest documents for {company_symbol}")
        
        documents = self.get_company_documents(company_symbol)
        
        results = {
            'company': company_symbol,
            'annual_reports': [],
            'transcripts': [],
            'errors': []
        }
        
        for report in documents['annual_reports'][:max_reports]:
            file_path = self.download_pdf_temp(report['pdf_url'], f"{company_symbol}_annual_{report['year']}")
            if file_path:
                results['annual_reports'].append({**report, 'local_path': file_path})
            else:
                results['errors'].append(f"Failed to download: {report['title']}")
        
        for concall in documents['concalls'][:max_transcripts]:
            if concall['transcript_url']:
                content = self.extract_transcript_content(concall['transcript_url'])
                if content:
                    results['transcripts'].append({
                        **concall,
                        'content': content[:1000] + "...",
                        'full_content': content,
                        'word_count': len(content.split())
                    })
                else:
                    results['errors'].append(f"Failed to extract transcript: {concall['date']}")
        
        logger.info(f"Complete: {len(results['annual_reports'])} PDFs, {len(results['transcripts'])} transcripts")
        return results
