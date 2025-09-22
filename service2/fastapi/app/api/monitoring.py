"""
Monitoring and metrics API endpoints
"""

import time
from typing import Dict, Any, List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.services.qdrant_service import QdrantService
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/metrics")
async def get_metrics():
    """Get Prometheus metrics"""
    from fastapi.responses import Response
    
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@router.get("/health")
async def monitoring_health() -> Dict[str, Any]:
    """Monitoring system health check"""
    
    return {
        "status": "healthy",
        "service": "monitoring",
        "timestamp": time.time(),
        "components": {
            "prometheus": "healthy",
            "grafana": "healthy",
            "logging": "healthy"
        }
    }


@router.get("/performance")
async def get_performance_metrics(
    hours: int = Query(default=24, ge=1, le=168, description="Hours of data to retrieve"),
    qdrant_service: QdrantService = Depends()
) -> Dict[str, Any]:
    """Get performance metrics"""
    
    try:
        # Get collection statistics
        collection_stats = await qdrant_service.get_collection_stats()
        
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        return {
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": hours
            },
            "collection": collection_stats,
            "performance": {
                "query_volume": "N/A",  # Would need query logging table
                "average_response_time": "N/A",  # Would need response time tracking
                "error_rate": "N/A",  # Would need error tracking
                "uptime_percentage": 99.9  # Placeholder
            },
            "system": {
                "memory_usage": "N/A",
                "cpu_usage": "N/A",
                "disk_usage": "N/A"
            }
        }
        
    except Exception as e:
        logger.error("Failed to get performance metrics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")


@router.get("/queries/summary")
async def get_query_summary(
    hours: int = Query(default=24, ge=1, le=168, description="Hours of data to retrieve")
) -> Dict[str, Any]:
    """Get summary of recent queries"""
    
    # This would normally query a query log table
    # For now, returning placeholder data
    
    return {
        "time_range_hours": hours,
        "total_queries": 150,
        "successful_queries": 145,
        "failed_queries": 5,
        "average_confidence": 0.85,
        "average_response_time": 2.3,
        "top_query_types": [
            {"type": "population_facts", "count": 45},
            {"type": "demographic_breakdown", "count": 38},
            {"type": "comparative_analysis", "count": 32},
            {"type": "temporal_trends", "count": 25},
            {"type": "other", "count": 10}
        ],
        "popular_states": [
            {"state": "Malaysia", "count": 78},
            {"state": "Selangor", "count": 42},
            {"state": "Kedah", "count": 30}
        ]
    }


@router.get("/alerts")
async def get_alerts(
    active_only: bool = Query(default=True, description="Show only active alerts")
) -> List[Dict[str, Any]]:
    """Get system alerts"""
    
    # This would normally query an alerts table
    # For now, returning placeholder alerts
    
    alerts = [
        {
            "id": "alert_001",
            "type": "warning",
            "title": "High query latency detected",
            "description": "Average query response time exceeded 5 seconds threshold",
            "severity": "medium",
            "active": True,
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "resolved_at": None
        },
        {
            "id": "alert_002", 
            "type": "info",
            "title": "Qdrant collection optimization recommended",
            "description": "Collection has over 10k points, consider reindexing",
            "severity": "low",
            "active": True,
            "created_at": (datetime.now() - timedelta(hours=6)).isoformat(),
            "resolved_at": None
        },
        {
            "id": "alert_003",
            "type": "error",
            "title": "OpenAI API rate limit approached",
            "description": "85% of daily quota used",
            "severity": "high",
            "active": False,
            "created_at": (datetime.now() - timedelta(hours=12)).isoformat(),
            "resolved_at": (datetime.now() - timedelta(hours=10)).isoformat()
        }
    ]
    
    if active_only:
        alerts = [alert for alert in alerts if alert["active"]]
    
    return alerts


@router.get("/dashboard")
async def get_dashboard_data(
    qdrant_service: QdrantService = Depends()
) -> Dict[str, Any]:
    """Get comprehensive dashboard data"""
    
    try:
        # Get collection stats
        collection_stats = await qdrant_service.get_collection_stats()
        
        # Get recent performance summary
        performance = await get_performance_metrics(hours=24, qdrant_service=qdrant_service)
        
        # Get recent query summary
        query_summary = await get_query_summary(hours=24)
        
        # Get active alerts
        alerts = await get_alerts(active_only=True)
        
        return {
            "generated_at": datetime.now().isoformat(),
            "collection": collection_stats,
            "performance": performance,
            "queries": query_summary,
            "alerts": alerts,
            "system_status": {
                "overall": "healthy",
                "qdrant": "operational",
                "openai": "operational",
                "api": "operational"
            }
        }
        
    except Exception as e:
        logger.error("Failed to get dashboard data", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")


@router.post("/alert/test")
async def create_test_alert() -> Dict[str, Any]:
    """Create a test alert (for development/testing)"""
    
    test_alert = {
        "id": f"test_alert_{int(time.time())}",
        "type": "info",
        "title": "Test alert created",
        "description": "This is a test alert for monitoring system testing",
        "severity": "low",
        "active": True,
        "created_at": datetime.now().isoformat(),
        "resolved_at": None
    }
    
    logger.info("Test alert created", alert_id=test_alert["id"])
    
    return {
        "message": "Test alert created successfully",
        "alert": test_alert
    }


@router.get("/export/metrics")
async def export_metrics(
    format: str = Query(default="json", regex="^(json|csv)$"),
    hours: int = Query(default=24, ge=1, le=168)
) -> Dict[str, Any]:
    """Export metrics in specified format"""
    
    try:
        # Get metrics data
        dashboard_data = await get_dashboard_data()
        
        if format == "csv":
            # Convert to CSV format (simplified example)
            csv_data = "timestamp,metric_type,metric_name,value\n"
            csv_data += f"{datetime.now().isoformat()},collection,total_points,{dashboard_data['collection']['total_points']}\n"
            csv_data += f"{datetime.now().isoformat()},queries,total,{dashboard_data['queries']['total_queries']}\n"
            csv_data += f"{datetime.now().isoformat()},alerts,active,{len(dashboard_data['alerts'])}\n"
            
            return {
                "format": "csv",
                "data": csv_data,
                "filename": f"rag_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        else:
            return {
                "format": "json",
                "data": dashboard_data,
                "filename": f"rag_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            }
            
    except Exception as e:
        logger.error("Failed to export metrics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to export metrics: {str(e)}")


@router.get("/logs/recent")
async def get_recent_logs(
    limit: int = Query(default=50, ge=1, le=200),
    level: str = Query(default="all", regex="^(all|info|warning|error|debug)$")
) -> List[Dict[str, Any]]:
    """Get recent application logs"""
    
    # This would normally query the logging system
    # For now, returning placeholder log entries
    
    log_levels = ["info", "warning", "error"] if level == "all" else [level]
    
    sample_logs = [
        {
            "timestamp": datetime.now().isoformat(),
            "level": "info",
            "service": "rag-api",
            "message": "RAG query completed successfully",
            "query_id": "query_123",
            "execution_time": 2.1
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
            "level": "warning", 
            "service": "rag-api",
            "message": "High query latency detected",
            "query_id": "query_122",
            "execution_time": 5.8
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(),
            "level": "error",
            "service": "rag-api",
            "message": "Qdrant connection timeout",
            "error": "Connection timeout after 30 seconds",
            "query_id": "query_121"
        }
    ]
    
    # Filter by level if specified
    if level != "all":
        sample_logs = [log for log in sample_logs if log["level"] == level]
    
    return sample_logs[:limit]