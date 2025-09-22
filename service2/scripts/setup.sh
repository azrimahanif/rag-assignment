#!/bin/bash

# Service2 Setup Script
# This script sets up the complete RAG system environment

set -e

echo "🚀 Setting up Service2 RAG Platform..."
echo "========================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/qdrant
mkdir -p data/redis
mkdir -p data/grafana
mkdir -p data/prometheus
mkdir -p data/elasticsearch
echo "✅ Directories created"

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment configuration..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual API keys and configurations"
fi

# Set permissions for scripts
echo "🔐 Setting permissions..."
chmod +x evaluation/evaluation-scripts.py
chmod +x qdrant/migration-scripts/migrate_data.py
echo "✅ Permissions set"

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose down 2>/dev/null || true
docker-compose build --no-cache
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

# Check Qdrant
if curl -f http://localhost:6333/ >/dev/null 2>&1; then
    echo "✅ Qdrant is running"
else
    echo "❌ Qdrant is not responding"
fi

# Check FastAPI
if curl -f http://localhost:8000/health/ >/dev/null 2>&1; then
    echo "✅ FastAPI is running"
else
    echo "❌ FastAPI is not responding"
fi

# Check n8n
if curl -f http://localhost:5678/ >/dev/null 2>&1; then
    echo "✅ n8n is running"
else
    echo "❌ n8n is not responding"
fi

# Check Redis
if redis-cli -h localhost -p 6379 ping >/dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "❌ Redis is not responding"
fi

# Check monitoring services
if curl -f http://localhost:3000/ >/dev/null 2>&1; then
    echo "✅ Grafana is running"
else
    echo "⚠️  Grafana is starting up..."
fi

if curl -f http://localhost:9090/ >/dev/null 2>&1; then
    echo "✅ Prometheus is running"
else
    echo "⚠️  Prometheus is starting up..."
fi

echo ""
echo "🎉 Service2 Setup Complete!"
echo "=========================="
echo ""
echo "🌐 Service URLs:"
echo "   - FastAPI:       http://localhost:8000"
echo "   - FastAPI Docs:  http://localhost:8000/docs"
echo "   - n8n:          http://localhost:5678"
echo "   - Qdrant:       http://localhost:6333"
echo "   - Grafana:      http://localhost:3000 (admin/admin)"
echo "   - Prometheus:   http://localhost:9090"
echo "   - Kibana:       http://localhost:5601"
echo ""
echo "📊 Monitoring:"
echo "   - Application logs: Check logs/ directory"
echo "   - Metrics: Prometheus + Grafana dashboards"
echo "   - Service health: Individual service endpoints"
echo ""
echo "🔧 Next Steps:"
echo "   1. Configure API keys in .env file"
echo "   2. Run data migration: docker-compose --profile migration up data-migration"
echo "   3. Import n8n workflows"
echo "   4. Test RAG functionality"
echo ""
echo "📚 Documentation:"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - n8n Workflows: http://localhost:5678"
echo "   - Service2 Directory: ./service2/"
echo ""