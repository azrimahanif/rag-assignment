# Deployment Guide

This guide provides comprehensive instructions for deploying the RAG Assignment system to various environments.

## 🎯 Deployment Overview

The RAG Assignment system can be deployed using multiple strategies depending on your requirements:

- **Local Development**: Single machine with all services running locally
- **Production Docker**: Containerized deployment with Docker Compose
- **Cloud Deployment**: Scalable cloud infrastructure deployment

### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Frontend      │    │   Backend       │
│   (Nginx/ALB)   │────│   (React)       │────│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│   Qdrant        │──────────────┘
                        │ Vector Database │
                        └─────────────────┘
                               │
                    ┌─────────────────┐
                    │   Monitoring    │
                    │  (Prometheus)    │
                    └─────────────────┘
```

## 🛠️ Prerequisites

### System Requirements

#### Minimum Requirements
- **CPU**: 4 cores
- **Memory**: 8GB RAM
- **Storage**: 50GB SSD
- **Network**: 100 Mbps
- **OS**: Ubuntu 20.04+, CentOS 8+, or equivalent

#### Recommended Requirements
- **CPU**: 8 cores
- **Memory**: 16GB RAM
- **Storage**: 100GB SSD
- **Network**: 1 Gbps
- **OS**: Ubuntu 22.04 LTS or equivalent

### Software Requirements
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: Latest version
- **OpenAI API Key**: For AI services
- **Domain Name**: For HTTPS configuration

### Environment Variables

Create a production `.env` file:

```bash
# Application Configuration
NODE_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# API Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FRONTEND_URL=https://your-domain.com

# Database Configuration
DATABASE_URL=postgresql://user:password@postgres:5432/rag_app
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=your-qdrant-api-key

# AI Services
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# External Services
DOSM_API_URL=https://api.dosm.gov.my
QUICKCHART_URL=https://quickchart.io

# Security
SECRET_KEY=your-secret-key-change-this
CORS_ORIGINS=https://your-domain.com

# Monitoring
ENABLE_METRICS=true
PROMETHEUS_ENDPOINT=http://prometheus:9090
```

## 🐳 Docker Deployment

### 1. Clone and Prepare Repository

```bash
git clone <repository-url>
cd RAG-Assignment

# Copy production configuration
cp docker-compose.prod.yml docker-compose.yml
cp .env.example .env

# Edit .env with production values
nano .env
```

### 2. Build and Deploy Services

```bash
# Build all services
docker-compose build

# Start services in detached mode
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 3. Initialize Data

```bash
# Run database migrations
docker-compose exec fastapi python -m alembic upgrade head

# Initialize vector database
docker-compose exec fastapi python prepare_data.py

# Verify data initialization
docker-compose exec fastapi python -c "from app.core.database import engine; print('Database connected')"
```

### 4. Configure Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/rag-app
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS headers
        add_header Access-Control-Allow-Origin https://your-domain.com;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept, Authorization";
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health checks
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
```

### 5. SSL/TLS Configuration

#### Using Let's Encrypt

```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

#### Manual SSL Configuration

1. Obtain SSL certificate from your provider
2. Place certificates in `/etc/ssl/certs/`
3. Update Nginx configuration with certificate paths
4. Test Nginx configuration: `sudo nginx -t`
5. Reload Nginx: `sudo systemctl reload nginx`

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS ECS (Elastic Container Service)

1. **Create ECR Repository**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Create repositories
aws ecr create-repository --repository-name rag-frontend
aws ecr create-repository --repository-name rag-backend
aws ecr create-repository --repository-name rag-qdrant
```

2. **Build and Push Images**
```bash
# Frontend
cd frontend
docker build -t rag-frontend .
docker tag rag-frontend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/rag-frontend:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/rag-frontend:latest

# Backend
cd service2
docker build -t rag-backend .
docker tag rag-backend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/rag-backend:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/rag-backend:latest
```

3. **Create ECS Task Definition**
```json
{
  "family": "rag-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "rag-backend",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/rag-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "NODE_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:OpenAI-API-Key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/rag-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

4. **Create ECS Service**
```bash
aws ecs create-service \
  --cluster rag-cluster \
  --service-name rag-app \
  --task-definition rag-app \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/rag-target/12345,containerName=rag-backend,containerPort=8000"
```

#### Using AWS RDS for Database

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier rag-app-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username raguser \
  --master-user-password your-password \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-12345 \
  --db-subnet-group-name rag-subnet-group

# Update environment variables
DATABASE_URL=postgresql://raguser:password@rag-app-db.12345.us-east-1.rds.amazonaws.com:5432/rag_app
```

### Google Cloud Platform Deployment

#### Using Google Cloud Run

1. **Build and Deploy to Cloud Run**
```bash
# Set project
gcloud config set project your-project-id

# Build and deploy frontend
cd frontend
gcloud builds submit --tag gcr.io/your-project-id/rag-frontend
gcloud run deploy rag-frontend \
  --image gcr.io/your-project-id/rag-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Build and deploy backend
cd service2
gcloud builds submit --tag gcr.io/your-project-id/rag-backend
gcloud run deploy rag-backend \
  --image gcr.io/your-project-id/rag-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars "OPENAI_API_KEY=your-key" \
  --no-allow-unauthenticated
```

2. **Set up Memorystore for Redis**
```bash
# Create Memorystore instance
gcloud redis instances create rag-redis \
  --region=us-central1 \
  --zone=us-central1-a \
  --redis-version=redis_6_x \
  --size=1 \
  --tier=standard

# Connect to Cloud Run
gcloud run services update rag-backend \
  --region=us-central1 \
  --set-env-vars "REDIS_URL=redis://10.0.0.3:6379"
```

## 🔍 Monitoring and Logging

### Monitoring Setup

#### Prometheus and Grafana

1. **Deploy Monitoring Stack**
```yaml
# docker-compose.yml monitoring section
monitoring:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--web.console.libraries=/etc/prometheus/console_libraries'
    - '--web.console.templates=/etc/prometheus/consoles'

grafana:
  image: grafana/grafana:latest
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
  volumes:
    - grafana-storage:/var/lib/grafana
```

2. **Prometheus Configuration**
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: ['fastapi:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

#### Application Metrics

Add metrics to your FastAPI application:

```python
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    # Record metrics
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(process_time)

    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Logging Configuration

#### Structured Logging

```python
import structlog
import logging

# Configure structlog
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

logger = structlog.get_logger()

@app.post("/api/v1/chat/message")
async def chat_message(message: str):
    logger.info("Processing chat message", session_id=session_id, message_length=len(message))

    try:
        result = await process_message(message)
        logger.info("Message processed successfully", session_id=session_id)
        return result
    except Exception as e:
        logger.error("Failed to process message", session_id=session_id, error=str(e))
        raise
```

#### Centralized Logging with ELK Stack

```yaml
# docker-compose.yml ELK section
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
  environment:
    - discovery.type=single-node
    - xpack.security.enabled=false
  ports:
    - "9200:9200"
  volumes:
    - elasticsearch-data:/usr/share/elasticsearch/data

logstash:
  image: docker.elastic.co/logstash/logstash:8.8.0
  volumes:
    - ./logstash/pipeline:/usr/share/logstash/pipeline
  depends_on:
    - elasticsearch

kibana:
  image: docker.elastic.co/kibana/kibana:8.8.0
  ports:
    - "5601:5601"
  depends_on:
    - elasticsearch
```

## 🔐 Security Configuration

### SSL/TLS Security

```nginx
# Strong SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_session_tickets off;

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

### Application Security

```python
# Security middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["your-domain.com", "www.your-domain.com"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Network Security

```yaml
# Docker network security
networks:
  app-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

# Firewall rules
services:
  fastapi:
    networks:
      - app-network
    ports:
      - "8000:8000"
    # Only allow connections from frontend
    extra_hosts:
      - "frontend:172.20.0.10"
```

## 🚀 Deployment Strategies

### Blue-Green Deployment

```bash
# Deploy new version (green)
docker-compose -f docker-compose.green.yml up -d

# Test green environment
curl https://green.your-domain.com/health

# Switch traffic
docker-compose -f docker-compose.blue.yml down
docker-compose -f docker-compose.green.yml up -d

# Update blue for next deployment
docker-compose -f docker-compose.blue.yml build
```

### Canary Deployment

```yaml
# Kubernetes canary deployment example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-app-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rag-app
      version: canary
  template:
    metadata:
      labels:
        app: rag-app
        version: canary
    spec:
      containers:
      - name: rag-app
        image: rag-app:v2.0.0
        ports:
        - containerPort: 8000
```

### Rolling Updates

```yaml
# docker-compose.yml with rolling update strategy
services:
  fastapi:
    image: rag-backend:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      rollback_config:
        parallelism: 0
        order: stop-first
```

## 📊 Backup and Recovery

### Database Backup

```bash
# PostgreSQL backup
docker exec postgres pg_dump -U raguser rag_app > backup_$(date +%Y%m%d_%H%M%S).sql

# Qdrant backup
docker exec qdrant qdrant-backup create /backups/backup_$(date +%Y%m%d_%H%M%S)

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR/$DATE

# Backup database
docker exec postgres pg_dump -U raguser rag_app > $BACKUP_DIR/$DATE/database.sql

# Backup Qdrant
docker exec qdrant qdrant-backup create /backups/$DATE/qdrant

# Compress backups
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz $BACKUP_DIR/$DATE/

# Remove old backups (keep 7 days)
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete
```

### Disaster Recovery

```bash
# Recovery script
#!/bin/bash
BACKUP_FILE=$1
RESTORE_DIR="/restore"

# Extract backup
tar -xzf $BACKUP_FILE -C $RESTORE_DIR

# Restore database
docker exec -i postgres psql -U raguser rag_app < $RESTORE_DIR/database.sql

# Restore Qdrant
docker exec qdrant qdrant-backup create /restore/qdrant

# Verify recovery
curl http://localhost:8000/health
```

## 🔧 Performance Optimization

### Load Balancing

```nginx
# Upstream configuration
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;

    # Load balancing methods
    least_conn;
    keepalive 32;
}

server {
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # Health checks
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
    }
}
```

### Caching Strategy

```python
from fastapi_cache import FastAPICache, Coder
from fastapi_cache.backends.redis import RedisBackend

@app.post("/api/v1/chat/message")
@cache(expire=300, key_builder=lambda *args, **kwargs: f"chat:{kwargs['message']}")
async def chat_message(message: str):
    return await process_message(message)
```

### Database Optimization

```python
# Connection pooling
DATABASE_URL = "postgresql://user:pass@host:5432/db?pool_size=10&max_overflow=20"

# Query optimization with indexes
CREATE INDEX CONCURRENTLY idx_messages_session_created ON chat_messages(session_id, created_at);
CREATE INDEX CONCURRENTLY idx_sources_relevance ON sources(relevance_score DESC);

# Read replicas for scaling
DATABASE_URL_READ = "postgresql://user:pass@read-replica:5432/db"
```

## 🧪 Testing and Validation

### Deployment Testing

```bash
# Health check script
#!/bin/bash
URL="https://your-domain.com"

# Test health endpoint
curl -f $URL/health || exit 1

# Test API endpoint
curl -f -X POST $URL/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}' || exit 1

# Test SSL/TLS
openssl s_client -connect your-domain.com:443 -servername your-domain.com < /dev/null

# Performance test
ab -n 1000 -c 10 https://your-domain.com/health
```

### Load Testing

```bash
# Using k6 for load testing
k6 run --vus 100 --duration 30s load-test.js

# load-test.js
import http from 'k6/http';
import { check } from 'k6';

export default function () {
    const response = http.post('https://your-domain.com/api/v1/chat/message', {
        message: 'What is Malaysia population?'
    });

    check(response, {
        'status is 200': (r) => r.status === 200,
        'response time < 2s': (r) => r.timings.duration < 2000,
    });
}
```

## 📈 Monitoring Dashboards

### Grafana Dashboard Setup

1. **Import Dashboard**
```json
{
  "dashboard": {
    "title": "RAG Application Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100"
          }
        ]
      }
    ]
  }
}
```

### Alert Configuration

```yaml
# prometheus-alerts.yml
groups:
- name: rag-app-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) > 0.05
    for: 10m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is above 5% for 10 minutes"

  - alert: HighResponseTime
    expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is above 2 seconds"
```

---

This deployment guide provides comprehensive instructions for deploying the RAG Assignment system in various environments. For additional support or questions, please refer to the project documentation or create an issue in the repository.