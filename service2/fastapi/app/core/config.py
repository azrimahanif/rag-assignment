"""
Application configuration settings
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings as PydanticBaseSettings


class Settings(PydanticBaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "RAG System"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=True, env="FASTAPI_DEBUG")
    HOST: str = Field(default="0.0.0.0", env="FASTAPI_HOST")
    PORT: int = Field(default=8000, env="FASTAPI_PORT")
    
    # Security
    SECRET_KEY: str = Field(default="dev-secret-key", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # Qdrant Configuration
    QDRANT_URL: str = Field(default="http://localhost:6333", env="QDRANT_URL")
    QDRANT_API_KEY: Optional[str] = Field(default=None, env="QDRANT_API_KEY")
    QDRANT_COLLECTION: str = Field(default="population_data", env="QDRANT_COLLECTION")
    QDRANT_TIMEOUT: int = Field(default=30, env="QDRANT_TIMEOUT")
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-ada-002", env="OPENAI_EMBEDDING_MODEL")
    OPENAI_CHAT_MODEL: str = Field(default="gpt-3.5-turbo", env="OPENAI_CHAT_MODEL")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_TIMEOUT: int = Field(default=5, env="REDIS_TIMEOUT")
    
    # Database
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./rag_app.db", env="DATABASE_URL")
    
    # Monitoring
    PROMETHEUS_URL: str = Field(default="http://localhost:9090", env="PROMETHEUS_URL")
    GRAFANA_URL: str = Field(default="http://localhost:3000", env="GRAFANA_URL")

    # Opik Configuration
    OPIK_URL: Optional[str] = Field(default=None, env="OPIK_URL")
    OPIK_API_KEY: Optional[str] = Field(default=None, env="OPIK_API_KEY")
    OPIK_WORKSPACE: Optional[str] = Field(default=None, env="OPIK_WORKSPACE")
    OPIK_PROJECT_NAME: str = Field(default="rag-system", env="OPIK_PROJECT_NAME")
    OPIK_ENABLED: bool = Field(default=True, env="OPIK_ENABLED")
    
    # Evaluation
    EVALUATION_API_URL: str = Field(default="http://localhost:8000", env="EVALUATION_API_URL")
    EVALUATION_TIMEOUT: int = Field(default=30, env="EVALUATION_TIMEOUT")
    EVALUATION_MAX_RETRIES: int = Field(default=3, env="EVALUATION_MAX_RETRIES")
    
    # Performance
    MAX_WORKERS: int = Field(default=4, env="MAX_WORKERS")
    REQUEST_TIMEOUT: int = Field(default=60, env="REQUEST_TIMEOUT")
    
    # RAG Configuration
    MAX_RESULTS: int = Field(default=5, env="MAX_RESULTS")
    SIMILARITY_THRESHOLD: float = Field(default=0.7, env="SIMILARITY_THRESHOLD")
    CHUNK_SIZE: int = Field(default=1000, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=200, env="CHUNK_OVERLAP")
    
    # Data Configuration
    DATA_DIR: str = Field(default="./data", env="DATA_DIR")
    DATA_CACHE_TTL: int = Field(default=3600, env="DATA_CACHE_TTL")  # 1 hour
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables
    
    @property
    def qdrant_client_config(self) -> dict:
        """Qdrant client configuration"""
        config = {
            "url": self.QDRANT_URL,
            "timeout": self.QDRANT_TIMEOUT,
        }
        if self.QDRANT_API_KEY:
            config["api_key"] = self.QDRANT_API_KEY
        return config
    
    @property
    def openai_client_config(self) -> dict:
        """OpenAI client configuration"""
        config = {}
        if self.OPENAI_API_KEY:
            config["api_key"] = self.OPENAI_API_KEY
        return config

    @property
    def opik_config(self) -> dict:
        """Opik configuration"""
        config = {
            "project_name": self.OPIK_PROJECT_NAME,
        }
        if self.OPIK_URL:
            config["url"] = self.OPIK_URL
        if self.OPIK_API_KEY:
            config["api_key"] = self.OPIK_API_KEY
        if self.OPIK_WORKSPACE:
            config["workspace"] = self.OPIK_WORKSPACE
        return config
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.DEBUG
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.DEBUG


# Global settings instance
settings = Settings()