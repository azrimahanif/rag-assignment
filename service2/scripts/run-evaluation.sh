#!/bin/bash

# Evaluation Script for RAG System
# This script runs the complete evaluation suite

set -e

echo "🧪 Running RAG System Evaluation..."
echo "================================="

# Check if services are running
echo "🏥 Checking service health..."
if ! curl -f http://localhost:8000/health/ >/dev/null 2>&1; then
    echo "❌ FastAPI is not running. Please start services first."
    exit 1
fi

echo "✅ Services are running"

# Change to evaluation directory
cd evaluation

# Run evaluation script
echo "🔍 Running evaluation queries..."
python3 evaluation-scripts.py

# Check if evaluation completed successfully
if [ $? -eq 0 ]; then
    echo "✅ Evaluation completed successfully"
    
    # Display results summary
    if [ -f "evaluation_results.json" ]; then
        echo ""
        echo "📊 Evaluation Results Summary:"
        echo "============================="
        
        # Extract key metrics using jq if available, otherwise show file location
        if command -v jq &> /dev/null; then
            echo "Total Queries: $(jq '.metrics.total_queries' evaluation_results.json)"
            echo "Success Rate: $(jq '.metrics.successful_queries' evaluation_results.json)/$(jq '.metrics.total_queries' evaluation_results.json)"
            echo "Average Latency: $(jq '.metrics.average_latency' evaluation_results.json)s"
            echo "Accuracy Score: $(jq '.metrics.accuracy_score' evaluation_results.json * 100 | jq 'floor/100')%"
        else
            echo "Detailed results available in: evaluation_results.json"
        fi
        
        echo ""
        echo "📈 Metrics Export:"
        echo "   - JSON format: evaluation_results.json"
        echo "   - CSV format: curl http://localhost:8000/api/v1/monitoring/export/metrics?format=csv"
    fi
else
    echo "❌ Evaluation failed"
    exit 1
fi

echo ""
echo "🎯 Additional Test Commands:"
echo "============================"
echo ""
echo "Test single query:"
echo "  curl -X POST http://localhost:8000/api/v1/rag/query \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"query\": \"What was Malaysia\\'s population in 2023?\"}'"
echo ""
echo "Health check:"
echo "  curl http://localhost:8000/health/detailed"
echo ""
echo "Collection info:"
echo "  curl http://localhost:8000/api/v1/rag/collection-info"
echo ""
echo "Performance metrics:"
echo "  curl http://localhost:8000/api/v1/monitoring/performance"
echo ""
echo "📊 Dashboard:"
echo "============="
echo "View comprehensive metrics at: http://localhost:3000 (Grafana)"
echo ""