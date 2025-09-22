# API Reference

This document provides detailed information about all API endpoints available in the RAG Assignment system.

## 📚 API Overview

The RAG Assignment system provides RESTful APIs for chat functionality, data retrieval, and system monitoring. All APIs use JSON for request and response bodies.

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

### Authentication
Currently, the API does not require authentication for development. For production deployment, implement appropriate authentication mechanisms.

### Response Format
All API responses follow this general structure:

```json
{
  "success": true,
  "data": {},
  "message": "Success message",
  "timestamp": "2025-09-22T10:30:00Z"
}
```

### Error Responses
Error responses follow this structure:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {}
  },
  "timestamp": "2025-09-22T10:30:00Z"
}
```

## 🗨️ Chat API

### Send Message

Process a user message and generate a response with relevant sources.

**Endpoint**: `POST /api/v1/chat/message`

**Request Body**:
```json
{
  "message": "What is Malaysia's population in 2024?",
  "session_id": "optional-session-identifier"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "session_id": "session_123456",
    "response": "Based on the data from DOSM, Malaysia's population in 2024 was approximately 33.9 million people.",
    "sources": [
      {
        "id": "source_1",
        "title": "DOSM Malaysia Population Data 2024",
        "content": "Population data for Malaysia in 2024...",
        "url": "https://dosm.gov.my/population-2024",
        "relevance_score": 0.95
      }
    ],
    "charts": [
      {
        "url": "https://quickchart.io/chart?...",
        "title": "Population Trends 2020-2024",
        "type": "line"
      }
    ]
  },
  "timestamp": "2025-09-22T10:30:00Z"
}
```

**Status Codes**:
- `200`: Success
- `400`: Invalid request parameters
- `500`: Internal server error

### Get Chat History

Retrieve all messages for a specific chat session.

**Endpoint**: `GET /api/v1/chat/history/{session_id}`

**Path Parameters**:
- `session_id` (string, required): Unique session identifier

**Response**:
```json
{
  "success": true,
  "data": {
    "session_id": "session_123456",
    "messages": [
      {
        "id": "msg_1",
        "role": "user",
        "content": "What is Malaysia's population?",
        "timestamp": "2025-09-22T10:28:00Z"
      },
      {
        "id": "msg_2",
        "role": "assistant",
        "content": "Based on DOSM data...",
        "timestamp": "2025-09-22T10:30:00Z",
        "sources": [...],
        "charts": [...]
      }
    ]
  },
  "timestamp": "2025-09-22T10:35:00Z"
}
```

**Status Codes**:
- `200`: Success
- `404`: Session not found
- `500`: Internal server error

### Create Chat Session

Create a new chat session with optional title.

**Endpoint**: `POST /api/v1/chat/session`

**Request Body**:
```json
{
  "title": "Population Research Session"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "session_id": "session_123456",
    "title": "Population Research Session",
    "created_at": "2025-09-22T10:30:00Z",
    "is_active": true
  },
  "timestamp": "2025-09-22T10:30:00Z"
}
```

**Status Codes**:
- `201`: Session created
- `400`: Invalid request
- `500`: Internal server error

### List Chat Sessions

Get all chat sessions for the user.

**Endpoint**: `GET /api/v1/chat/sessions`

**Query Parameters**:
- `limit` (int, optional): Maximum number of sessions (default: 50)
- `offset` (int, optional): Number of sessions to skip (default: 0)

**Response**:
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "session_id": "session_123456",
        "title": "Population Research Session",
        "created_at": "2025-09-22T10:30:00Z",
        "message_count": 5,
        "last_activity": "2025-09-22T10:45:00Z"
      }
    ],
    "total": 1,
    "limit": 50,
    "offset": 0
  },
  "timestamp": "2025-09-22T10:50:00Z"
}
```

**Status Codes**:
- `200`: Success
- `500`: Internal server error

### Delete Chat Session

Delete a chat session and all associated messages.

**Endpoint**: `DELETE /api/v1/chat/session/{session_id}`

**Path Parameters**:
- `session_id` (string, required): Session identifier to delete

**Response**:
```json
{
  "success": true,
  "data": {
    "session_id": "session_123456",
    "deleted": true,
    "messages_deleted": 5
  },
  "timestamp": "2025-09-22T10:55:00Z"
}
```

**Status Codes**:
- `200`: Success
- `404`: Session not found
- `500`: Internal server error

## 📊 Data API

### Search Population Data

Search for population data based on query parameters.

**Endpoint**: `GET /api/v1/data/search`

**Query Parameters**:
- `query` (string, required): Search query text
- `year` (int, optional): Filter by specific year
- `state` (string, optional): Filter by state (Malaysia, Kedah, Selangor)
- `age_group` (string, optional): Filter by age group
- `limit` (int, optional): Maximum results (default: 10)

**Response**:
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "data_1",
        "state": "Malaysia",
        "year": 2024,
        "age_group": "overall",
        "sex": "both",
        "ethnicity": "overall",
        "population": 33942.9,
        "data_source": "malaysia_api",
        "score": 0.95
      }
    ],
    "total": 1,
    "query": "Malaysia population 2024",
    "filters_applied": {
      "year": 2024,
      "state": "Malaysia"
    }
  },
  "timestamp": "2025-09-22T11:00:00Z"
}
```

**Status Codes**:
- `200`: Success
- `400`: Invalid parameters
- `500`: Internal server error

### Get Data Sources

Retrieve all available data sources with metadata.

**Endpoint**: `GET /api/v1/data/sources`

**Response**:
```json
{
  "success": true,
  "data": {
    "sources": [
      {
        "id": "malaysia_api",
        "name": "DOSM Malaysia API",
        "description": "Official DOSM API for Malaysia population data",
        "coverage": "1970-2025",
        "update_frequency": "Annual",
        "record_count": 35830,
        "last_updated": "2025-09-22T00:00:00Z"
      },
      {
        "id": "state_parquet",
        "name": "State Parquet Files",
        "description": "State-level population data in Parquet format",
        "coverage": "1970-2025",
        "states": ["Kedah", "Selangor"],
        "record_count": 25100,
        "last_updated": "2025-09-22T00:00:00Z"
      }
    ]
  },
  "timestamp": "2025-09-22T11:05:00Z"
}
```

**Status Codes**:
- `200`: Success
- `500`: Internal server error

### Get Data Statistics

Get statistical information about the population dataset.

**Endpoint**: `GET /api/v1/data/statistics`

**Response**:
```json
{
  "success": true,
  "data": {
    "total_records": 35830,
    "time_range": {
      "start_year": 1970,
      "end_year": 2025
    },
    "geographic_coverage": [
      "Malaysia",
      "Kedah",
      "Selangor"
    ],
    "demographic_breakdown": {
      "age_groups": 21,
      "sex_categories": 3,
      "ethnicity_categories": 9
    },
    "data_quality": {
      "completeness": 98.5,
      "accuracy": 99.2,
      "timeliness": 95.0
    },
    "last_updated": "2025-09-22T00:00:00Z"
  },
  "timestamp": "2025-09-22T11:10:00Z"
}
```

**Status Codes**:
- `200`: Success
- `500`: Internal server error

## 🏥 Health API

### Basic Health Check

Check if the service is running and basic functionality is working.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-22T11:15:00Z",
  "version": "1.0.0",
  "uptime": 3600
}
```

**Status Codes**:
- `200`: Healthy
- `503`: Service unavailable

### Detailed Health Check

Comprehensive health check including all dependencies.

**Endpoint**: `GET /health/detailed`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-22T11:20:00Z",
  "version": "1.0.0",
  "uptime": 3600,
  "components": {
    "database": {
      "status": "healthy",
      "response_time": 0.005,
      "connection_count": 1,
      "max_connections": 10
    },
    "qdrant": {
      "status": "healthy",
      "response_time": 0.150,
      "collections_count": 1,
      "vectors_count": 35830
    },
    "openai": {
      "status": "healthy",
      "response_time": 0.800,
      "rate_limit_remaining": 999,
      "model": "gpt-3.5-turbo"
    },
    "external_apis": {
      "dosm": {
        "status": "healthy",
        "response_time": 0.300
      },
      "quickchart": {
        "status": "healthy",
        "response_time": 0.200
      }
    }
  },
  "metrics": {
    "cpu_usage": 15.5,
    "memory_usage": 512.0,
    "disk_usage": 25.3
  }
}
```

**Status Codes**:
- `200`: Healthy
- `503`: One or more components unhealthy

### Readiness Check

Check if the service is ready to accept traffic.

**Endpoint**: `GET /health/ready`

**Response**:
```json
{
  "ready": true,
  "checks": {
    "database": true,
    "qdrant": true,
    "openai": true,
    "initialization_complete": true
  },
  "timestamp": "2025-09-22T11:25:00Z"
}
```

**Status Codes**:
- `200`: Ready
- `503`: Not ready

### Liveness Check

Check if the service is alive and responding.

**Endpoint**: `GET /health/live`

**Response**:
```json
{
  "alive": true,
  "timestamp": "2025-09-22T11:30:00Z"
}
```

**Status Codes**:
- `200`: Alive
- `503`: Not alive

## 📈 Monitoring API

### Get Performance Metrics

Retrieve system performance metrics.

**Endpoint**: `GET /api/v1/monitoring/metrics`

**Response**:
```json
{
  "success": true,
  "data": {
    "system": {
      "cpu_percent": 15.5,
      "memory_percent": 45.2,
      "disk_percent": 25.3,
      "load_average": [1.2, 1.1, 1.0]
    },
    "api": {
      "requests_per_minute": 120,
      "average_response_time": 0.450,
      "error_rate": 0.5,
      "active_connections": 25
    },
    "rag": {
      "average_query_time": 0.800,
      "retrieval_accuracy": 0.92,
      "generation_time": 0.300,
      "cache_hit_rate": 0.75
    },
    "database": {
      "query_average_time": 0.005,
      "connection_pool_usage": 0.1,
      "slow_queries_count": 0
    }
  },
  "timestamp": "2025-09-22T11:35:00Z"
}
```

**Status Codes**:
- `200**: Success
- `500`: Internal server error

### Get Application Logs

Retrieve application logs with filtering capabilities.

**Endpoint**: `GET /api/v1/monitoring/logs`

**Query Parameters**:
- `level` (string, optional): Log level (DEBUG, INFO, WARNING, ERROR)
- `limit` (int, optional): Maximum log entries (default: 100)
- `offset` (int, optional): Number of entries to skip (default: 0)
- `start_time` (string, optional): Start time filter (ISO format)
- `end_time` (string, optional): End time filter (ISO format)

**Response**:
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "timestamp": "2025-09-22T11:40:00Z",
        "level": "INFO",
        "message": "Chat message processed successfully",
        "module": "chat_service",
        "session_id": "session_123456",
        "request_id": "req_789"
      },
      {
        "timestamp": "2025-09-22T11:41:00Z",
        "level": "ERROR",
        "message": "Failed to connect to Qdrant",
        "module": "qdrant_service",
        "error": "Connection timeout"
      }
    ],
    "total": 2,
    "filters": {
      "level": null,
      "limit": 100,
      "offset": 0
    }
  },
  "timestamp": "2025-09-22T11:45:00Z"
}
```

**Status Codes**:
- `200`: Success
- `400`: Invalid parameters
- `500**: Internal server error

## 🔄 WebSocket API

### Real-time Chat Updates

Receive real-time updates for chat messages and system status.

**Endpoint**: `ws://localhost:8000/ws/chat/{session_id}`

**Message Format**:
```json
{
  "type": "message_update",
  "data": {
    "session_id": "session_123456",
    "message": {
      "id": "msg_789",
      "role": "assistant",
      "content": "Processing your query...",
      "timestamp": "2025-09-22T11:50:00Z"
    }
  }
}
```

**Message Types**:
- `message_update`: New message or update
- `typing_start`: User started typing
- `typing_stop`: User stopped typing
- `system_status`: System status update
- `error`: Error notification

## 📋 Error Codes

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `AUTHENTICATION_ERROR` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Access denied |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

### Error Response Examples

#### Validation Error
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "message",
      "issue": "Message cannot be empty"
    }
  },
  "timestamp": "2025-09-22T11:55:00Z"
}
```

#### Rate Limit Error
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests",
    "details": {
      "retry_after": 60,
      "limit": "100 requests per minute"
    }
  },
  "timestamp": "2025-09-22T12:00:00Z"
}
```

## 🔄 Rate Limiting

### Rate Limits

- **Chat API**: 100 requests per minute per session
- **Data API**: 200 requests per minute per IP
- **Health API**: No rate limiting
- **Monitoring API**: 60 requests per minute per IP

### Rate Limit Headers

All API responses include rate limiting headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1641234567
```

## 🔒 Security Considerations

### Input Validation
- All inputs are sanitized and validated
- Maximum request body size: 10MB
- Maximum message length: 10,000 characters
- SQL injection protection implemented

### Data Protection
- No sensitive data logged
- Secure storage of session data
- HTTPS required in production
- CORS properly configured

### Best Practices
- Use HTTPS in production
- Implement proper authentication
- Validate all input parameters
- Handle errors gracefully
- Monitor for suspicious activity

---

This API reference provides comprehensive information for integrating with the RAG Assignment system. For additional support or questions, please refer to the project documentation or create an issue in the repository.