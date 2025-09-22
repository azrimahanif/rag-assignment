# Service2: Complete RAG Platform

A comprehensive, production-ready Retrieval-Augmented Generation (RAG) platform with integrated workflow automation, monitoring, and evaluation capabilities.

## 🚀 Features

- **🔍 RAG System**: Advanced retrieval-augmented generation for population data
- **🗄️ Vector Database**: Self-hosted Qdrant with optimized indexing
- **⚡ FastAPI Backend**: High-performance REST API with comprehensive endpoints
- **🔄 Workflow Automation**: n8n integration for automated processes
- **📊 Monitoring**: Prometheus + Grafana + ELK stack for complete observability
- **🧪 Evaluation Framework**: Comprehensive testing and quality assessment
- **📈 Performance Metrics**: Real-time tracking of accuracy, latency, and system health
- **🐳 Docker Compose**: One-command deployment with all services

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Frontend    │    │    FastAPI      │    │      n8n        │
│   (React App)   │────│     Backend     │────│  Workflows      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│     Qdrant      │──────────────┘
                        │ Vector Database │
                        └─────────────────┘

```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 8GB+ RAM
- OpenAI API Key (for embeddings)
- Python 3.11+ (for local development)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd RAG-Assignment/service2
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start Services
```bash
# Run the setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Or manually:
docker-compose up -d
```

### 3. Migrate Data
```bash
# Run data migration
docker-compose --profile migration up data-migration
```

### 4. Access Services
- **FastAPI API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **n8n Workflows**: http://localhost:5678
- **Qdrant Management**: http://localhost:6333

## 📊 Service Endpoints

### FastAPI RAG API
```
POST /api/v1/rag/query           # Main RAG query endpoint
POST /api/v1/rag/embedding       # Create text embeddings
GET  /api/v1/rag/search          # Search documents
GET  /api/v1/rag/collection-info # Collection statistics
POST /api/v1/rag/validate-answer # Answer validation
GET  /api/v1/rag/health          # RAG health check
```

### Health Monitoring
```
GET  /health/                    # Basic health check
GET  /health/detailed            # Detailed health with dependencies
GET  /health/ready               # Readiness check
GET  /health/live                # Liveness check
```

### Monitoring & Metrics
```
GET  /api/v1/monitoring/metrics  # Prometheus metrics
GET  /api/v1/monitoring/performance # Performance stats
GET  /api/v1/monitoring/dashboard  # Dashboard data
GET  /api/v1/monitoring/alerts     # System alerts
```

## 🧪 Evaluation Framework

### Running Evaluation Tests
```bash
# Run complete evaluation suite
./scripts/run-evaluation.sh

# Or manually:
cd evaluation
python3 evaluation-scripts.py
```

### Test Queries
The evaluation framework includes 15 carefully designed queries:

1. **Simple Factual**: "What was Malaysia's population in 2023?"
2. **Demographic Breakdown**: "Show age distribution in Kedah for 2023"
3. **Comparative Analysis**: "Compare populations of Kedah and Selangor"
4. **Temporal Trends**: "Population growth over last 10 years"
5. **Complex Multi-step**: "Dependency ratio analysis in Selangor"

### Metrics Tracked
- **Latency**: p50/p95 response times
- **Accuracy**: Factual correctness assessment
- **Retrieval Hit Rate**: Document retrieval effectiveness
- **Hallucination Rate**: Made-up information detection
- **Source Citation**: Proper attribution tracking

## 📈 Monitoring Stack

### Grafana Dashboards
- **System Health**: CPU, memory, disk usage
- **RAG Performance**: Query latency, accuracy scores
- **API Metrics**: Request rates, error rates
- **Database Metrics**: Qdrant performance, indexing stats

### Log Aggregation
- **ELK Stack**: Elasticsearch + Logstash + Kibana
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Centralized Monitoring**: All services log to central system

### Alerting
- **Slack Integration**: Real-time notifications
- **Email Alerts**: Critical system issues
- **Dashboard Alerts**: Visual warnings in Grafana

## 🔧 Configuration

### Environment Variables
```bash
# API Keys
OPENAI_API_KEY=your-openai-api-key
QDRANT_API_KEY=your-qdrant-api-key

# Service Configuration
N8N_USERNAME=admin
N8N_PASSWORD=your-password
GRAFANA_PASSWORD=admin

# Database
REDIS_URL=redis://redis:6379
DATABASE_URL=sqlite:///./rag_app.db
```

### Service Scaling
```yaml
# docker-compose.yml
services:
  fastapi:
    deploy:
      replicas: 2
    environment:
      - MAX_WORKERS=4
```

## 🔄 n8n Workflows

### Included Workflows
1. **RAG Query Processing**: Automated query handling and logging
2. **Data Validation**: Scheduled data quality checks
3. **Alert Management**: System alert routing and escalation

### Custom Workflows
- Import workflows from `n8n/workflows/`
- Configure webhooks and API integrations
- Set up scheduled tasks and automation

## 📚 Data Card

### Dataset Information
- **Source**: DOSM Malaysia Population Data
- **Coverage**: 1970-2025, Malaysia + 2 states
- **Records**: 35,830 individual data points
- **Demographics**: Age, sex, ethnicity breakdowns
- **Quality**: Official government statistics

See `data-card.md` for complete dataset documentation.

## 🧩 Development

### Local Development
```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Run tests
pytest tests/

# Lint code
black app/
flake8 app/
mypy app/
```

### Adding New Features
1. Update FastAPI endpoints in `fastapi/app/api/`
2. Add services in `fastapi/app/services/`
3. Create n8n workflows in `n8n/workflows/`
4. Update monitoring metrics
5. Add evaluation tests

## 🚀 Deployment

### Production Deployment
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose --profile migration up data-migration
```

### Infrastructure Requirements
- **Minimum**: 8GB RAM, 4 CPU cores, 50GB storage
- **Recommended**: 16GB RAM, 8 CPU cores, 100GB SSD
- **Network**: Stable internet connection for API access

## 🔍 Troubleshooting

### Common Issues

**Services Not Starting**
```bash
# Check logs
docker-compose logs fastapi
docker-compose logs qdrant
docker-compose logs n8n

# Restart services
docker-compose restart
```

**API Key Issues**
```bash
# Verify .env file
cat .env

# Test API connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

**Memory Issues**
```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
services:
  fastapi:
    mem_limit: 4g
```

## 📝 API Usage Examples

### Basic RAG Query
```bash
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What was Malaysia population in 2023?",
    "max_results": 5
  }'
```

### Search with Filters
```bash
curl -X GET "http://localhost:8000/api/v1/rag/search?query=Selangor&state=Selangor&year=2024"
```

### Health Check
```bash
curl http://localhost:8000/health/detailed
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **DOSM Malaysia** for the population data
- **Qdrant Team** for the vector database
- **n8n** for workflow automation
- **FastAPI** for the web framework
- **OpenAI** for AI services

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in `/docs/`
- Review troubleshooting section above

---

**Service2 Version**: 1.0.0  
**Last Updated**: September 2025  
**Maintainers**: RAG Development Team