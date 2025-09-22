"""
Qdrant vector database service
"""

import time
from typing import List, Dict, Any, Optional
import asyncio

from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct, 
    VectorParams, 
    Distance, 
    Filter,
    FieldCondition,
    MatchValue,
    Range
)
from qdrant_client.http.models import CollectionInfo

from app.core.config import settings
from app.core.logging import get_logger, log_execution_time

logger = get_logger(__name__)


class QdrantService:
    """Service for Qdrant vector database operations"""
    
    def __init__(self):
        self.client: Optional[QdrantClient] = None
        self.collection_name = settings.QDRANT_COLLECTION
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Qdrant client"""
        try:
            self.client = QdrantClient(**settings.qdrant_client_config)
            logger.info("Qdrant client initialized", url=settings.QDRANT_URL)
        except Exception as e:
            logger.error("Failed to initialize Qdrant client", error=str(e))
            raise
    
    @log_execution_time(logger, "qdrant_health_check")
    async def health_check(self) -> Dict[str, Any]:
        """Check Qdrant service health"""
        start_time = time.time()
        
        try:
            # Test basic connectivity
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "collections_count": len(collection_names),
                "collections": collection_names,
                "collection_exists": self.collection_name in collection_names
            }
            
        except Exception as e:
            logger.error("Qdrant health check failed", error=str(e))
            raise
    
    async def ensure_collection_exists(self) -> bool:
        """Ensure the target collection exists"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                logger.info("Creating collection", collection=self.collection_name)
                
                # Create collection with appropriate vector size
                vector_size = 1536  # OpenAI ada-002 embedding size
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                
                # Create payload indexes for better filtering
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="metadata.state",
                    field_schema="keyword"
                )
                
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="metadata.year",
                    field_schema="integer"
                )
                
                logger.info("Collection created successfully", collection=self.collection_name)
                return True
            else:
                logger.info("Collection already exists", collection=self.collection_name)
                return False
                
        except Exception as e:
            logger.error("Failed to ensure collection exists", error=str(e))
            raise
    
    @log_execution_time(logger, "qdrant_search")
    async def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        filter_conditions: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in Qdrant"""
        
        try:
            # Build query filter if conditions provided
            query_filter = None
            if filter_conditions:
                query_filter = self._build_filter(filter_conditions)
            
            # Perform search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=query_filter,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False
            )
            
            # Format results
            results = []
            for hit in search_result:
                result = {
                    "id": hit.id,
                    "score": hit.score,
                    "text": hit.payload.get("text", ""),
                    "metadata": hit.payload.get("metadata", {}),
                    "source": hit.payload.get("metadata", {}).get("data_source", "unknown")
                }
                results.append(result)
            
            logger.info(
                "Search completed",
                results_count=len(results),
                query_filter=filter_conditions,
                score_threshold=score_threshold
            )
            
            return results
            
        except Exception as e:
            logger.error("Search failed", error=str(e))
            raise
    
    @log_execution_time(logger, "qdrant_upsert")
    async def upsert_points(self, points: List[PointStruct]) -> bool:
        """Upsert points into Qdrant"""
        
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info("Points upserted successfully", count=len(points))
            return True
            
        except Exception as e:
            logger.error("Failed to upsert points", error=str(e))
            raise
    
    @log_execution_time(logger, "qdrant_delete")
    async def delete_points(self, point_ids: List[str]) -> bool:
        """Delete points from Qdrant"""
        
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=point_ids
            )
            
            logger.info("Points deleted successfully", count=len(point_ids))
            return True
            
        except Exception as e:
            logger.error("Failed to delete points", error=str(e))
            raise
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information"""
        
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            return {
                "name": self.collection_name,
                "vectors_count": collection_info.points_count,
                "vectors_config": collection_info.config.params.vectors,
                "status": collection_info.status,
                "optimizer_status": collection_info.optimizer_status,
                "indexed_vectors_count": collection_info.indexed_vectors_count
            }
            
        except Exception as e:
            logger.error("Failed to get collection info", error=str(e))
            raise
    
    async def count_points(self, filter_conditions: Optional[Dict[str, Any]] = None) -> int:
        """Count points in collection with optional filter"""
        
        try:
            query_filter = None
            if filter_conditions:
                query_filter = self._build_filter(filter_conditions)
            
            count = self.client.count(
                collection_name=self.collection_name,
                count_filter=query_filter
            )
            
            return count.count
            
        except Exception as e:
            logger.error("Failed to count points", error=str(e))
            raise
    
    def _build_filter(self, conditions: Dict[str, Any]) -> Filter:
        """Build Qdrant filter from conditions"""
        
        must_conditions = []
        
        for field, value in conditions.items():
            if isinstance(value, dict):
                # Handle range conditions
                if "gte" in value or "lte" in value:
                    range_condition = Range(
                        key=field,
                        gte=value.get("gte"),
                        lte=value.get("lte")
                    )
                    must_conditions.append(FieldCondition(key=field, range=range_condition))
            else:
                # Handle exact match
                must_conditions.append(
                    FieldCondition(key=field, match=MatchValue(value=value))
                )
        
        return Filter(must=must_conditions)
    
    async def clear_collection(self) -> bool:
        """Clear all points from collection"""
        
        try:
            self.client.delete_collection(self.collection_name)
            
            # Recreate collection
            await self.ensure_collection_exists()
            
            logger.info("Collection cleared successfully", collection=self.collection_name)
            return True
            
        except Exception as e:
            logger.error("Failed to clear collection", error=str(e))
            raise
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get comprehensive collection statistics"""
        
        try:
            collection_info = await self.get_collection_info()
            total_count = await self.count_points()
            
            # Get stats by state
            states = ["Malaysia", "Kedah", "Selangor"]
            state_counts = {}
            
            for state in states:
                state_count = await self.count_points({"metadata.state": state})
                state_counts[state] = state_count
            
            # Get stats by year range
            current_year = 2024
            year_ranges = {
                "recent_5_years": (current_year - 4, current_year),
                "recent_10_years": (current_year - 9, current_year),
                "historical": (1970, current_year - 10)
            }
            
            year_stats = {}
            for range_name, (start_year, end_year) in year_ranges.items():
                year_count = await self.count_points({
                    "metadata.year": {"gte": start_year, "lte": end_year}
                })
                year_stats[range_name] = year_count
            
            return {
                "collection_info": collection_info,
                "total_points": total_count,
                "state_distribution": state_counts,
                "temporal_distribution": year_stats,
                "average_points_per_year": total_count / max(1, current_year - 1970 + 1)
            }
            
        except Exception as e:
            logger.error("Failed to get collection stats", error=str(e))
            raise