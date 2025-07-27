# Troubleshooting Guide

## Common Setup Issues

### Database Connection Problems

#### MySQL Connection Failed

**Error**: `MySQL connection failed: Access denied for user 'root'@'localhost'`

**Solution**:
```bash
# 1. Check MySQL is running
brew services list | grep mysql  # macOS
sudo systemctl status mysql      # Linux

# 2. Reset MySQL password
sudo mysql
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
EXIT;

# 3. Update .env file
MYSQL_PASSWORD=new_password

# 4. Test connection
mysql -u root -p -e "SELECT 1;"
```

#### Database Does Not Exist

**Error**: `Unknown database 'financial_forecasting'`

**Solution**:
```bash
mysql -u root -p -e "CREATE DATABASE financial_forecasting;"
```

#### Connection Timeout

**Error**: `Lost connection to MySQL server during query`

**Solution**:
```sql
-- Increase timeout settings
SET GLOBAL wait_timeout = 600;
SET GLOBAL interactive_timeout = 600;
SET GLOBAL max_allowed_packet = 67108864;  -- 64MB
```

### LLM Provider Issues

#### Ollama Not Found

**Error**: `No LLM providers available`

**Solutions**:
```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Start Ollama service
ollama serve

# 3. Download model (in another terminal)
ollama pull llama3.1:8b

# 4. Verify installation
ollama list
ollama run llama3.1:8b "Hello"
```

#### OpenAI API Issues

**Error**: `OpenAI API key invalid`

**Solutions**:
```bash
# 1. Check API key format
# Should start with sk-proj- or sk-
echo $OPENAI_API_KEY

# 2. Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# 3. Check billing/quota
# Visit https://platform.openai.com/usage
```

#### Rate Limiting

**Error**: `Rate limit exceeded`

**Solutions**:
```python
# Add retry logic with exponential backoff
import time
import random

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                raise
```

### PDF Processing Issues

#### PDF Download Fails

**Error**: `Failed to download PDF from URL`

**Solutions**:
```python
# 1. Check internet connection
curl -I https://www.screener.in

# 2. Verify PDF URL accessibility
curl -I "https://example.com/report.pdf"

# 3. Add user agent to requests
headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; FinancialBot/1.0)'
}
```

#### PDF Parsing Errors

**Error**: `No financial tables found in PDF`

**Solutions**:
```python
# 1. Debug PDF structure
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    for page in pdf.pages[:3]:  # Check first 3 pages
        print(f"Page {page.page_number}:")
        print(page.extract_text()[:500])

# 2. Lower financial keyword threshold
FINANCIAL_KEYWORDS_THRESHOLD = 1  # Instead of 2

# 3. Check for image-based PDFs
# These may need OCR processing
```

#### Memory Issues with Large PDFs

**Error**: `MemoryError during PDF processing`

**Solutions**:
```python
# 1. Process pages incrementally
def process_pdf_incrementally(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # Process one page at a time
            yield process_page(page)
            
            # Clear memory every 10 pages
            if page_num % 10 == 0:
                import gc
                gc.collect()

# 2. Limit PDF size
MAX_PDF_SIZE = 50 * 1024 * 1024  # 50MB limit
```

### Vector Store Issues

#### ChromaDB Collection Errors

**Error**: `Collection already exists`

**Solutions**:
```python
# 1. Delete and recreate collection
try:
    client.delete_collection("earnings_transcripts")
except:
    pass
collection = client.create_collection("earnings_transcripts")

# 2. Use get_or_create pattern
try:
    collection = client.get_collection("earnings_transcripts")
except:
    collection = client.create_collection("earnings_transcripts")
```

#### Poor Search Results

**Error**: `Enhanced search: 0 quality chunks found`

**Solutions**:
```python
# 1. Lower similarity threshold
results = vectorstore.search_transcripts(
    query="outlook", 
    min_similarity=0.0  # Accept all results
)

# 2. Debug chunk quality
def debug_chunks(vectorstore):
    stats = vectorstore.get_collection_stats()
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Quality distribution: {stats.get('quality_status')}")

# 3. Improve chunking strategy
MIN_CHUNK_LENGTH = 50    # Reduce from 150
MIN_WORDS = 10           # Reduce from 20
```

#### Embedding Model Issues

**Error**: `sentence-transformers model download failed`

**Solutions**:
```bash
# 1. Clear model cache
rm -rf ~/.cache/huggingface/transformers/

# 2. Download manually
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
"

# 3. Use alternative model
ALTERNATIVE_MODEL = "paraphrase-MiniLM-L6-v2"
```

## Performance Issues

### Slow Request Processing

#### Issue: Requests taking >5 minutes

**Diagnostic Steps**:
```python
# 1. Add timing to each component
import time

def timed_operation(operation_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            print(f"{operation_name}: {duration:.2f}s")
            return result
        return wrapper
    return decorator

@timed_operation("Financial Extraction")
def extract_financial_data(self, ...):
    # Your code here
```

**Common Bottlenecks**:
1. **PDF Download**: 30-60 seconds per large PDF
2. **Table Extraction**: 60-120 seconds for 300+ page PDFs
3. **LLM Processing**: 10-30 seconds per call
4. **Vector Search**: 1-5 seconds with large collections

**Optimization Solutions**:
```python
# 1. Cache downloaded PDFs
def get_cached_pdf(url, cache_dir="data/downloads"):
    cache_file = os.path.join(cache_dir, hashlib.md5(url.encode()).hexdigest() + ".pdf")
    if os.path.exists(cache_file):
        return cache_file
    # Download and cache

# 2. Limit PDF processing
MAX_PAGES_TO_PROCESS = 50  # Process first 50 pages only
MAX_TABLES_TO_ANALYZE = 10  # Analyze top 10 tables only

# 3. Parallel processing where possible
import asyncio

async def parallel_data_gathering():
    tasks = [
        extract_financial_data(),
        analyze_transcripts(),
        fetch_market_data()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### Memory Usage Issues

#### Issue: High memory consumption

**Diagnostic Commands**:
```bash
# Monitor memory usage
top -p $(pgrep -f "uvicorn")
htop

# Python memory profiling
pip install memory-profiler
python -m memory_profiler app/main.py
```

**Memory Optimization**:
```python
# 1. Clear variables after use
def process_large_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        tables = extract_tables(pdf)
        result = process_tables(tables)
        
        # Clear large objects
        del tables
        import gc
        gc.collect()
        
        return result

# 2. Stream processing for large files
def stream_pdf_processing(pdf_path):
    for page_batch in paginate_pdf(pdf_path, batch_size=10):
        yield process_batch(page_batch)
        # Memory freed after each batch

# 3. Limit concurrent requests
from asyncio import Semaphore

MAX_CONCURRENT_REQUESTS = 3
request_semaphore = Semaphore(MAX_CONCURRENT_REQUESTS)

async def rate_limited_forecast(request):
    async with request_semaphore:
        return await generate_forecast(request)
```

### Database Performance

#### Slow Query Performance

**Diagnostic Queries**:
```sql
-- Check slow queries
SHOW VARIABLES LIKE 'slow_query_log';
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- Monitor current queries
SHOW PROCESSLIST;

-- Check index usage
EXPLAIN SELECT * FROM forecast_requests WHERE company_symbol = 'TCS';
```

**Optimization Solutions**:
```sql
-- Add missing indexes
CREATE INDEX idx_company_created ON forecast_requests(company_symbol, created_at);
CREATE INDEX idx_success_created ON forecast_requests(success, created_at);

-- Optimize queries
-- Instead of:
SELECT * FROM forecast_requests WHERE company_symbol = 'TCS';

-- Use:
SELECT id, company_symbol, created_at FROM forecast_requests 
WHERE company_symbol = 'TCS' 
ORDER BY created_at DESC 
LIMIT 10;

-- Archive old data
CREATE TABLE forecast_requests_archive LIKE forecast_requests;
INSERT INTO forecast_requests_archive 
SELECT * FROM forecast_requests 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);

DELETE FROM forecast_requests 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);
```

## System Health Monitoring

### Application Health Checks

```python
# Comprehensive health check
async def detailed_system_check():
    checks = {
        "database": check_database_health(),
        "llm_provider": check_llm_health(),
        "vector_store": check_vector_store_health(),
        "external_apis": check_external_apis_health(),
        "disk_space": check_disk_space(),
        "memory": check_memory_usage()
    }
    
    results = {}
    for name, check in checks.items():
        try:
            results[name] = await check
        except Exception as e:
            results[name] = {"status": "error", "error": str(e)}
    
    return results

async def check_database_health():
    try:
        start_time = time.time()
        await db_manager.connection.execute("SELECT 1")
        response_time = time.time() - start_time
        
        return {
            "status": "healthy",
            "response_time_ms": round(response_time * 1000, 2)
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### Log Analysis

```bash
# Find error patterns
grep -i error /var/log/financial-forecasting.log | head -20

# Monitor request rates
grep "POST /forecast" /var/log/nginx/access.log | wc -l

# Check processing times
grep "processing_time" /var/log/financial-forecasting.log | \
  awk -F'"processing_time":' '{print $2}' | \
  awk -F',' '{print $1}' | \
  sort -n | tail -10
```

### Performance Monitoring Scripts

```bash
#!/bin/bash
# System monitoring script

# CPU usage
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)

# Memory usage
mem_usage=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')

# Disk usage
disk_usage=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)

# Active connections
active_connections=$(netstat -an | grep :8000 | grep ESTABLISHED | wc -l)

echo "CPU: ${cpu_usage}%, Memory: ${mem_usage}%, Disk: ${disk_usage}%, Connections: ${active_connections}"

# Alert if thresholds exceeded
if (( $(echo "$cpu_usage > 80" | bc -l) )); then
    echo "ALERT: High CPU usage: ${cpu_usage}%"
fi
```

## Recovery Procedures

### Application Recovery

```bash
#!/bin/bash
# Application restart script

# Stop application
pkill -f uvicorn

# Clear any stuck processes
pkill -f "python.*financial"

# Clear cache if corrupted
rm -rf data/vector_store/__pycache__
rm -rf data/downloads/*.tmp

# Restart with fresh environment
source .venv/bin/activate
export $(cat .env | xargs)
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Wait for startup
sleep 10

# Verify health
curl -f http://localhost:8000/health || exit 1

echo "Application restarted successfully"
```

### Database Recovery

```bash
#!/bin/bash
# Database recovery script

# Check if MySQL is running
if ! pgrep mysql > /dev/null; then
    echo "Starting MySQL..."
    brew services start mysql  # or systemctl start mysql
fi

# Test connection
if ! mysql -u root -p -e "SELECT 1;" > /dev/null 2>&1; then
    echo "Database connection failed"
    exit 1
fi

# Check database exists
if ! mysql -u root -p -e "USE financial_forecasting;" > /dev/null 2>&1; then
    echo "Creating database..."
    mysql -u root -p -e "CREATE DATABASE financial_forecasting;"
fi

# Verify tables exist
mysql -u root -p financial_forecasting -e "SHOW TABLES;"

echo "Database recovery completed"
```

### Data Recovery

```python
# Recover from backup
def restore_from_backup(backup_file):
    """Restore vector store from backup"""
    import tarfile
    import shutil
    
    # Stop application first
    print("Stopping application...")
    
    # Clear current data
    if os.path.exists("data/vector_store"):
        shutil.rmtree("data/vector_store")
    
    # Extract backup
    with tarfile.open(backup_file, "r:gz") as tar:
        tar.extractall("data/")
    
    print(f"Restored from backup: {backup_file}")
    print("Restart application to use restored data")
```

## Development and Testing

### Local Development Issues

#### Port Already in Use

```bash
# Find process using port 8000
lsof -ti:8000

# Kill process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --port 8001
```

#### Import Errors

```python
# Add project root to Python path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Or use relative imports
from ..models import FinancialMetrics
```

### Testing Environment

```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt

# Use test database
export MYSQL_DATABASE=financial_forecasting_test

# Run with test data
export TEST_MODE=true
uvicorn app.main:app --reload
```

## Emergency Procedures

### System Down

1. **Check basic connectivity**:
   ```bash
   curl -I http://localhost:8000/health
   ```

2. **Check processes**:
   ```bash
   ps aux | grep uvicorn
   ps aux | grep mysql
   ```

3. **Check logs**:
   ```bash
   tail -f /var/log/financial-forecasting.log
   journalctl -u mysql -f
   ```

4. **Restart services**:
   ```bash
   systemctl restart mysql
   pkill -f uvicorn
   uvicorn app.main:app --host 0.0.0.0 --port 8000 &
   ```

### Data Corruption

1. **Stop application immediately**
2. **Assess damage**:
   ```bash
   # Check database integrity
   mysqlcheck --check --all-databases
   
   # Check vector store
   ls -la data/vector_store/
   ```

3. **Restore from backup**:
   ```bash
   # Database restore
   mysql financial_forecasting < backup.sql
   
   # Vector store restore
   tar -xzf vector_store_backup.tar.gz -C data/
   ```

4. **Verify restoration**:
   ```bash
   curl http://localhost:8000/health
   ```

### Performance Crisis

1. **Immediate relief**:
   ```bash
   # Limit concurrent requests
   nginx -s reload  # With updated rate limits
   
   # Scale up resources
   docker-compose up --scale app=3
   ```

2. **Identify bottleneck**:
   ```bash
   # Monitor system resources
   htop
   iotop
   
   # Check database performance
   mysql -e "SHOW PROCESSLIST;"
   ```

3. **Apply quick fixes**:
   ```python
   # Reduce processing scope
   MAX_REPORTS_TO_DOWNLOAD = 1
   MAX_TRANSCRIPTS_TO_PROCESS = 1
   MAX_TABLES_TO_ANALYZE = 5
   ```

Remember: Always test recovery procedures in a non-production environment first!