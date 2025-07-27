# Production Deployment Guide

## Production Environment Setup

### Database Configuration

#### MySQL Production Setup

```sql
-- Create production database and user
CREATE DATABASE financial_forecasting;
CREATE USER 'forecast_user'@'%' IDENTIFIED BY 'secure_production_password';
GRANT ALL PRIVILEGES ON financial_forecasting.* TO 'forecast_user'@'%';
FLUSH PRIVILEGES;

-- Optimize for production
SET GLOBAL innodb_buffer_pool_size = 1073741824;  -- 1GB
SET GLOBAL max_connections = 200;
SET GLOBAL query_cache_size = 67108864;  -- 64MB
```

#### Production Environment Variables

```bash
# Production .env
MYSQL_HOST=your-production-db-host.com
MYSQL_USER=forecast_user
MYSQL_PASSWORD=secure_production_password
MYSQL_DATABASE=financial_forecasting

# Production LLM configuration
OPENAI_API_KEY=sk-your-production-openai-key
LOG_LEVEL=WARNING

# Optional: Additional production settings
API_WORKERS=4
MAX_CONNECTIONS=100
```

### Docker Deployment

#### Dockerfile

```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MYSQL_HOST=db
      - MYSQL_USER=forecast_user
      - MYSQL_PASSWORD=secure_password
      - MYSQL_DATABASE=financial_forecasting
    depends_on:
      - db
    restart: unless-stopped
    volumes:
      - ./data:/app/data
    
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: financial_forecasting
      MYSQL_USER: forecast_user
      MYSQL_PASSWORD: secure_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql-init:/docker-entrypoint-initdb.d
    restart: unless-stopped

volumes:
  mysql_data:
```

### Kubernetes Deployment

#### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: financial-forecasting-agent
  labels:
    app: financial-forecasting-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: financial-forecasting-agent
  template:
    metadata:
      labels:
        app: financial-forecasting-agent
    spec:
      containers:
      - name: app
        image: your-registry/financial-forecasting-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: MYSQL_HOST
          value: "mysql-service"
        - name: MYSQL_USER
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: username
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: password
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-secret
              key: openai-key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: financial-forecasting-service
spec:
  selector:
    app: financial-forecasting-agent
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

### Cloud Provider Configurations

#### AWS Deployment

```bash
# ECS Task Definition
{
  "family": "financial-forecasting-agent",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "financial-forecasting-agent",
      "image": "your-account.dkr.ecr.region.amazonaws.com/financial-forecasting-agent:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "MYSQL_HOST",
          "value": "your-rds-endpoint.region.rds.amazonaws.com"
        }
      ],
      "secrets": [
        {
          "name": "MYSQL_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:mysql-password"
        }
      ]
    }
  ]
}
```

#### Google Cloud Platform

```yaml
# Cloud Run Service
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: financial-forecasting-agent
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/cpu-throttling: "false"
        run.googleapis.com/memory: "2Gi"
        run.googleapis.com/cpu: "1000m"
    spec:
      containers:
      - image: gcr.io/your-project/financial-forecasting-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: MYSQL_HOST
          value: "your-cloud-sql-ip"
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: password
```

## Security Configuration

### API Security

#### Authentication Setup

```python
# Add to app/main.py
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Implement JWT verification logic
    if not verify_jwt_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

# Protect endpoints
@app.post("/forecast")
async def generate_forecast(request: ForecastRequest, token: str = Depends(verify_token)):
    # Your existing code
```

#### Rate Limiting

```python
# Add rate limiting middleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/forecast")
@limiter.limit("5/minute")  # 5 requests per minute
async def generate_forecast(request: Request, forecast_request: ForecastRequest):
    # Your existing code
```

### Database Security

#### SSL Configuration

```python
# MySQL SSL connection
import pymysql

ssl_config = {
    'ssl': {
        'ca': '/path/to/ca-cert.pem',
        'cert': '/path/to/client-cert.pem',
        'key': '/path/to/client-key.pem'
    }
}

connection = pymysql.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE,
    **ssl_config
)
```

#### Data Encryption

```python
# Encrypt sensitive data before storage
from cryptography.fernet import Fernet

class EncryptedDatabase:
    def __init__(self, encryption_key):
        self.cipher = Fernet(encryption_key)
    
    def encrypt_data(self, data):
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

### Network Security

#### HTTPS Configuration

```nginx
# Nginx configuration
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring and Observability

### Application Monitoring

#### Prometheus Metrics

```python
# Add to app/main.py
from prometheus_client import Counter, Histogram, generate_latest
import time

# Metrics
REQUEST_COUNT = Counter('forecast_requests_total', 'Total forecast requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('forecast_request_duration_seconds', 'Request latency')

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_LATENCY.observe(time.time() - start_time)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

#### Logging Configuration

```python
# Structured logging for production
import structlog
import json

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

### Infrastructure Monitoring

#### Health Checks

```python
# Enhanced health check
@app.get("/health/detailed")
async def detailed_health_check():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {}
    }
    
    # Database health
    try:
        await db_manager.get_request_stats()
        health_status["components"]["database"] = "healthy"
    except Exception:
        health_status["components"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # LLM health
    try:
        from app.main import get_agent
        agent = get_agent()
        health_status["components"]["agent"] = "healthy"
    except Exception:
        health_status["components"]["agent"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # External APIs
    try:
        import yfinance as yf
        yf.Ticker("TCS.NS").info  # Quick test
        health_status["components"]["market_data"] = "healthy"
    except Exception:
        health_status["components"]["market_data"] = "unhealthy"
    
    return health_status
```

#### Alerting

```yaml
# Prometheus alerting rules
groups:
- name: financial-forecasting-agent
  rules:
  - alert: HighErrorRate
    expr: rate(forecast_requests_total{status="error"}[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      
  - alert: HighLatency
    expr: histogram_quantile(0.95, forecast_request_duration_seconds) > 300
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High latency detected"
      
  - alert: ServiceDown
    expr: up{job="financial-forecasting-agent"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Service is down"
```

## Performance Optimization

### Caching Strategies

#### Redis Integration

```python
# Add Redis caching
import redis
import json
from datetime import timedelta

redis_client = redis.Redis(host='localhost', port=6379, db=0)

class CacheManager:
    def __init__(self):
        self.redis = redis_client
        self.default_ttl = 3600  # 1 hour
    
    async def get_cached_forecast(self, company_symbol: str):
        cache_key = f"forecast:{company_symbol}"
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def cache_forecast(self, company_symbol: str, forecast_data: dict):
        cache_key = f"forecast:{company_symbol}"
        self.redis.setex(
            cache_key, 
            self.default_ttl, 
            json.dumps(forecast_data, default=str)
        )
```

#### Database Optimization

```sql
-- Add indexes for better performance
CREATE INDEX idx_forecast_requests_company ON forecast_requests(company_symbol);
CREATE INDEX idx_forecast_requests_created ON forecast_requests(created_at);
CREATE INDEX idx_forecast_requests_success ON forecast_requests(success);

-- Partition large tables by date
ALTER TABLE forecast_requests PARTITION BY RANGE (YEAR(created_at)) (
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

### Load Balancing

#### Nginx Configuration

```nginx
upstream financial_forecasting_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://financial_forecasting_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 300s;  # Long timeout for forecast generation
    }
}
```

## Backup and Disaster Recovery

### Database Backup

```bash
#!/bin/bash
# Automated MySQL backup script

BACKUP_DIR="/var/backups/mysql"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="financial_forecasting_backup_$DATE.sql"

# Create backup
mysqldump -u root -p financial_forecasting > "$BACKUP_DIR/$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_DIR/$BACKUP_FILE"

# Upload to cloud storage (example: AWS S3)
aws s3 cp "$BACKUP_DIR/$BACKUP_FILE.gz" s3://your-backup-bucket/mysql/

# Clean up old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete
```

### Application State Backup

```python
# Backup vector store and configuration
import shutil
import tarfile
from datetime import datetime

def backup_application_state():
    backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"/var/backups/app/app_state_{backup_time}.tar.gz"
    
    with tarfile.open(backup_path, "w:gz") as tar:
        tar.add("data/vector_store", arcname="vector_store")
        tar.add(".env", arcname="config/env")
        tar.add("data/logs", arcname="logs")
    
    return backup_path
```

## Compliance and Auditing

### Audit Logging

```python
# Enhanced audit logging
class AuditLogger:
    def __init__(self):
        self.logger = structlog.get_logger("audit")
    
    def log_forecast_request(self, user_id: str, company_symbol: str, 
                           ip_address: str, result: dict):
        self.logger.info(
            "forecast_generated",
            user_id=user_id,
            company_symbol=company_symbol,
            ip_address=ip_address,
            recommendation=result.get("investment_recommendation"),
            confidence=result.get("analyst_confidence"),
            processing_time=result.get("processing_time")
        )
```

### Data Retention

```sql
-- Implement data retention policy
DELIMITER //
CREATE EVENT cleanup_old_requests
ON SCHEDULE EVERY 1 DAY
DO
BEGIN
    DELETE FROM forecast_requests 
    WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);
END //
DELIMITER ;
```

## Cost Optimization

### Resource Management

```python
# Dynamic resource scaling based on load
class ResourceManager:
    def __init__(self):
        self.max_workers = 4
        self.current_load = 0
    
    def scale_workers(self, current_requests: int):
        if current_requests > 10:
            return min(self.max_workers, current_requests // 3)
        return 1
```

### API Cost Management

```python
# LLM cost tracking
class CostTracker:
    def __init__(self):
        self.costs = {
            "openai": {"gpt-4": 0.03, "gpt-3.5": 0.002},
            "anthropic": {"claude-3": 0.025}
        }
    
    def track_llm_usage(self, provider: str, model: str, tokens: int):
        cost = self.costs.get(provider, {}).get(model, 0) * tokens / 1000
        # Log cost for billing
        structlog.get_logger().info("llm_cost", provider=provider, model=model, tokens=tokens, cost=cost)
```