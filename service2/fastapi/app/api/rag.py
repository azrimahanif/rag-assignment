"""
RAG (Retrieval-Augmented Generation) API endpoints
"""

import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, Query
from prometheus_client import Histogram, Gauge

from app.services.qdrant_service import QdrantService
from app.services.openai_service import OpenAIService
from app.services.opik_service import get_opik_service, track_llm_call, log_llm_metadata
from app.core.logging import get_logger, log_execution_time

router = APIRouter()
logger = get_logger(__name__)

# Prometheus metrics
RAG_QUERY_DURATION = Histogram('rag_query_duration_seconds', 'RAG query duration')
RAG_CONFIDENCE_SCORE = Gauge('rag_confidence_score', 'RAG confidence score')
RAG_RETRIEVAL_COUNT = Gauge('rag_retrieval_count', 'Number of documents retrieved')


class QueryRequest(BaseModel):
    """RAG query request model"""
    query: str = Field(..., description="User query")
    max_results: int = Field(default=5, ge=1, le=20, description="Maximum number of results")
    filter_state: Optional[str] = Field(None, description="Filter by state (Malaysia, Kedah, Selangor)")
    filter_year: Optional[int] = Field(None, description="Filter by year")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Similarity threshold")


class QueryResponse(BaseModel):
    """RAG query response model"""
    query: str
    answer: str
    confidence: float
    sources: List[str]
    context_chunks: int
    execution_time: float
    metadata: Dict[str, Any]


class EmbeddingRequest(BaseModel):
    """Embedding request model"""
    text: str = Field(..., description="Text to embed")


class EmbeddingResponse(BaseModel):
    """Embedding response model"""
    embedding: List[float]
    model: str
    dimensions: int


@track_llm_call("rag_query_pipeline", tags=["rag", "pipeline", "query"])
@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    qdrant_service: QdrantService = Depends(),
    openai_service: OpenAIService = Depends()
) -> QueryResponse:
    """Main RAG query endpoint"""
    
    start_time = time.time()
    
    try:
        logger.info("RAG query started", query=request.query, max_results=request.max_results)

        # Log initial RAG pipeline metadata
        log_llm_metadata({
            "query": request.query,
            "max_results": request.max_results,
            "filter_state": request.filter_state,
            "filter_year": request.filter_year,
            "similarity_threshold": request.similarity_threshold
        })

        # Step 1: Create query embedding
        query_embedding = await openai_service.create_embedding(request.query)

        # Step 2: Build filter conditions
        filter_conditions = {}
        if request.filter_state:
            filter_conditions["metadata.state"] = request.filter_state
        if request.filter_year:
            filter_conditions["metadata.year"] = request.filter_year

        # Step 3: Search Qdrant for relevant documents
        search_results = await qdrant_service.search(
            query_vector=query_embedding,
            limit=request.max_results,
            filter_conditions=filter_conditions if filter_conditions else None,
            score_threshold=request.similarity_threshold
        )

        RAG_RETRIEVAL_COUNT.set(len(search_results))

        if not search_results:
            logger.warning("No search results found", query=request.query)
            # Log metadata for no results case
            log_llm_metadata({
                "search_results_count": 0,
                "filter_conditions": filter_conditions,
                "query_answered": False,
                "reason": "No search results found"
            })
            return QueryResponse(
                query=request.query,
                answer="I don't have enough relevant information to answer this question.",
                confidence=0.0,
                sources=[],
                context_chunks=0,
                execution_time=time.time() - start_time,
                metadata={"search_results": 0, "filter_conditions": filter_conditions}
            )

        # Step 4: Extract context chunks
        context_chunks = [result["text"] for result in search_results]
        sources = list(set([result["source"] for result in search_results]))

        # Step 5: Generate answer using OpenAI
        rag_response = await openai_service.answer_with_context(
            query=request.query,
            context_chunks=context_chunks,
            temperature=0.3,
            max_tokens=800
        )

        execution_time = time.time() - start_time
        RAG_QUERY_DURATION.observe(execution_time)
        RAG_CONFIDENCE_SCORE.set(rag_response["confidence"])

        # Log final RAG pipeline metadata
        log_llm_metadata({
            "search_results_count": len(search_results),
            "context_chunks_count": len(context_chunks),
            "unique_sources_count": len(sources),
            "rag_confidence": rag_response["confidence"],
            "execution_time": execution_time,
            "total_tokens": rag_response.get("usage", {}).get("total_tokens", 0),
            "top_score": search_results[0]["score"] if search_results else 0.0,
            "query_answered": True,
            "filter_conditions": filter_conditions
        })

        logger.info(
            "RAG query completed",
            query=request.query,
            results_count=len(search_results),
            confidence=rag_response["confidence"],
            execution_time=execution_time
        )

        return QueryResponse(
            query=request.query,
            answer=rag_response["content"],
            confidence=rag_response["confidence"],
            sources=sources,
            context_chunks=len(context_chunks),
            execution_time=execution_time,
            metadata={
                "search_results": len(search_results),
                "filter_conditions": filter_conditions,
                "usage": rag_response.get("usage", {}),
                "top_score": search_results[0]["score"] if search_results else 0.0
            }
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error("RAG query failed", query=request.query, error=str(e))
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.post("/embedding", response_model=EmbeddingResponse)
async def create_embedding(
    request: EmbeddingRequest,
    openai_service: OpenAIService = Depends()
) -> EmbeddingResponse:
    """Create embedding for text"""
    
    try:
        logger.info("Creating embedding", text_length=len(request.text))
        
        embedding = await openai_service.create_embedding(request.text)
        
        return EmbeddingResponse(
            embedding=embedding,
            model="text-embedding-ada-002",
            dimensions=len(embedding)
        )
        
    except Exception as e:
        logger.error("Failed to create embedding", error=str(e))
        raise HTTPException(status_code=500, detail=f"Embedding creation failed: {str(e)}")


@router.post("/batch-embedding")
async def create_batch_embeddings(
    texts: List[str],
    openai_service: OpenAIService = Depends()
) -> Dict[str, Any]:
    """Create embeddings for multiple texts"""
    
    try:
        logger.info("Creating batch embeddings", texts_count=len(texts))
        
        embeddings = await openai_service.create_batch_embeddings(texts)
        
        return {
            "embeddings": embeddings,
            "model": "text-embedding-ada-002",
            "count": len(embeddings),
            "dimensions": len(embeddings[0]) if embeddings else 0
        }
        
    except Exception as e:
        logger.error("Failed to create batch embeddings", error=str(e))
        raise HTTPException(status_code=500, detail=f"Batch embedding creation failed: {str(e)}")


@router.get("/search")
async def search_documents(
    query: str = Query(..., description="Search query"),
    limit: int = Query(default=5, ge=1, le=20, description="Maximum results"),
    state: Optional[str] = Query(None, description="Filter by state"),
    year: Optional[int] = Query(None, description="Filter by year"),
    qdrant_service: QdrantService = Depends(),
    openai_service: OpenAIService = Depends()
) -> Dict[str, Any]:
    """Search for documents without generating an answer"""
    
    try:
        logger.info("Document search started", query=query, limit=limit)
        
        # Create query embedding
        query_embedding = await openai_service.create_embedding(query)
        
        # Build filter conditions
        filter_conditions = {}
        if state:
            filter_conditions["metadata.state"] = state
        if year:
            filter_conditions["metadata.year"] = year
        
        # Search Qdrant
        search_results = await qdrant_service.search(
            query_vector=query_embedding,
            limit=limit,
            filter_conditions=filter_conditions if filter_conditions else None,
            score_threshold=0.5
        )
        
        return {
            "query": query,
            "results": search_results,
            "count": len(search_results),
            "filter_conditions": filter_conditions
        }
        
    except Exception as e:
        logger.error("Document search failed", query=query, error=str(e))
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/collection-info")
async def get_collection_info(
    qdrant_service: QdrantService = Depends()
) -> Dict[str, Any]:
    """Get information about the Qdrant collection"""
    
    try:
        collection_info = await qdrant_service.get_collection_info()
        collection_stats = await qdrant_service.get_collection_stats()
        
        return {
            "collection": collection_info,
            "statistics": collection_stats
        }
        
    except Exception as e:
        logger.error("Failed to get collection info", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get collection info: {str(e)}")


@router.post("/validate-answer")
async def validate_answer(
    question: str,
    answer: str,
    context: str,
    openai_service: OpenAIService = Depends()
) -> Dict[str, Any]:
    """Validate an answer against provided context"""
    
    try:
        logger.info("Validating answer", question_length=len(question))
        
        validation_result = await openai_service.validate_answer(
            question=question,
            answer=answer,
            context=context
        )
        
        return validation_result
        
    except Exception as e:
        logger.error("Answer validation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/health")
async def rag_health_check(
    qdrant_service: QdrantService = Depends(),
    openai_service: OpenAIService = Depends()
) -> Dict[str, Any]:
    """Health check for RAG components"""
    
    try:
        qdrant_health = await qdrant_service.health_check()
        openai_health = await openai_service.health_check()
        
        return {
            "status": "healthy" if qdrant_health["status"] == "healthy" and openai_health["status"] == "healthy" else "degraded",
            "qdrant": qdrant_health,
            "openai": openai_health,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error("RAG health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }