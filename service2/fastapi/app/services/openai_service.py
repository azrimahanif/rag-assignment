"""
OpenAI service for embeddings and chat completions
"""

import time
from typing import List, Dict, Any, Optional

import openai
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import get_logger, log_execution_time
from app.services.opik_service import track_llm_call, log_llm_metadata

logger = get_logger(__name__)


class OpenAIService:
    """Service for OpenAI API interactions"""
    
    def __init__(self):
        self.client: Optional[AsyncOpenAI] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            if not settings.OPENAI_API_KEY:
                logger.warning("OpenAI API key not configured")
                return
            
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialized")
            
        except Exception as e:
            logger.error("Failed to initialize OpenAI client", error=str(e))
            raise
    
    @log_execution_time(logger, "openai_health_check")
    async def health_check(self) -> Dict[str, Any]:
        """Check OpenAI service health"""
        
        if not self.client:
            return {
                "status": "unconfigured",
                "error": "OpenAI API key not configured",
                "response_time": 0,
                "models_available": []
            }
        
        start_time = time.time()
        
        try:
            # Test API connectivity by listing models
            models = await self.client.models.list()
            model_names = [model.id for model in models.data]
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "models_available": model_names[:10],  # First 10 models
                "total_models": len(model_names)
            }
            
        except Exception as e:
            logger.error("OpenAI health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": time.time() - start_time,
                "models_available": []
            }
    
    @track_llm_call("create_embedding", tags=["openai", "embedding"])
    @log_execution_time(logger, "openai_embedding")
    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text"""
        
        if not self.client:
            raise ValueError("OpenAI client not initialized")
        
        try:
            response = await self.client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=text
            )

            embedding = response.data[0].embedding
            token_usage = response.usage

            # Log metadata to Opik
            log_llm_metadata({
                "model": settings.OPENAI_EMBEDDING_MODEL,
                "tokens_used": token_usage.total_tokens,
                "text_length": len(text),
                "input_text": text[:100] + "..." if len(text) > 100 else text
            })

            logger.info(
                "Embedding created",
                model=settings.OPENAI_EMBEDDING_MODEL,
                tokens_used=token_usage.total_tokens,
                text_length=len(text)
            )

            return embedding
            
        except Exception as e:
            logger.error("Failed to create embedding", error=str(e))
            raise
    
    @track_llm_call("create_batch_embeddings", tags=["openai", "embedding", "batch"])
    @log_execution_time(logger, "openai_batch_embeddings")
    async def create_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts"""
        
        if not self.client:
            raise ValueError("OpenAI client not initialized")
        
        if not texts:
            return []
        
        try:
            response = await self.client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=texts
            )

            embeddings = [item.embedding for item in response.data]
            token_usage = response.usage

            # Log metadata to Opik
            log_llm_metadata({
                "model": settings.OPENAI_EMBEDDING_MODEL,
                "texts_count": len(texts),
                "tokens_used": token_usage.total_tokens,
                "input_preview": texts[:2] if texts else []  # First 2 texts for preview
            })

            logger.info(
                "Batch embeddings created",
                model=settings.OPENAI_EMBEDDING_MODEL,
                texts_count=len(texts),
                tokens_used=token_usage.total_tokens
            )

            return embeddings
            
        except Exception as e:
            logger.error("Failed to create batch embeddings", error=str(e))
            raise
    
    @track_llm_call("create_chat_completion", tags=["openai", "chat", "completion"])
    @log_execution_time(logger, "openai_chat_completion")
    async def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Create chat completion"""
        
        if not self.client:
            raise ValueError("OpenAI client not initialized")
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_CHAT_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )

            if stream:
                # Handle streaming response
                return {"stream": response, "type": "stream"}

            # Handle non-streaming response
            completion = {
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }

            # Log metadata to Opik
            log_llm_metadata({
                "model": settings.OPENAI_CHAT_MODEL,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream,
                "messages_count": len(messages),
                "prompt_tokens": completion["usage"]["prompt_tokens"],
                "completion_tokens": completion["usage"]["completion_tokens"],
                "total_tokens": completion["usage"]["total_tokens"],
                "finish_reason": completion["finish_reason"],
                "input_preview": messages[-1]["content"][:100] + "..." if len(messages[-1]["content"]) > 100 else messages[-1]["content"]
            })

            logger.info(
                "Chat completion created",
                model=settings.OPENAI_CHAT_MODEL,
                tokens_used=completion["usage"]["total_tokens"],
                finish_reason=completion["finish_reason"]
            )

            return completion
            
        except Exception as e:
            logger.error("Failed to create chat completion", error=str(e))
            raise
    
    async def create_rag_prompt(
        self,
        query: str,
        context: str,
        max_context_length: int = 3000
    ) -> str:
        """Create RAG prompt with context"""
        
        # Truncate context if too long
        if len(context) > max_context_length:
            context = context[:max_context_length] + "..."
        
        system_prompt = f"""You are a helpful assistant that provides accurate information about Malaysian population data.

Context information is provided below. Use this context to answer the user's question accurately. If the context doesn't contain the information needed, say so clearly.

Context:
{context}

Instructions:
1. Base your answer only on the provided context
2. Include specific numbers and percentages when available
3. Cite the data source when possible
4. If information is not in the context, say "I don't have enough information to answer this question"
5. Be concise but thorough
6. Use thousands (k) or millions for large numbers as appropriate

User Question: {query}
"""
        
        return system_prompt
    
    @track_llm_call("answer_with_context", tags=["openai", "rag", "answer"])
    async def answer_with_context(
        self,
        query: str,
        context_chunks: List[str],
        temperature: float = 0.3,
        max_tokens: int = 800
    ) -> Dict[str, Any]:
        """Answer question using provided context chunks"""
        
        if not context_chunks:
            return {
                "content": "I don't have enough relevant information to answer this question.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Combine context chunks
        combined_context = "\n\n".join(context_chunks)
        
        # Create prompt
        prompt = await self.create_rag_prompt(query, combined_context)
        
        # Create messages for chat completion
        messages = [
            {"role": "system", "content": "You are a helpful assistant that provides accurate information about Malaysian population data."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Generate response
            completion = await self.create_chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract sources from context chunks
            sources = []
            for chunk in context_chunks:
                if "Source:" in chunk:
                    source_line = chunk.split("Source:")[1].split("\n")[0].strip()
                    sources.append(source_line)
            
            # Calculate confidence based on context relevance
            confidence = min(len(context_chunks) / 3.0, 1.0)  # More chunks = higher confidence
            
            result = {
                "content": completion["content"],
                "sources": list(set(sources)),  # Remove duplicates
                "confidence": confidence,
                "context_chunks_count": len(context_chunks),
                "usage": completion["usage"]
            }

            # Log metadata to Opik
            log_llm_metadata({
                "query": query,
                "context_chunks_count": len(context_chunks),
                "confidence": confidence,
                "sources_count": len(sources),
                "temperature": temperature,
                "max_tokens": max_tokens,
                "total_tokens": completion["usage"]["total_tokens"],
                "context_preview": context_chunks[0][:200] + "..." if context_chunks else "No context"
            })

            logger.info(
                "RAG answer generated",
                query_length=len(query),
                context_chunks=len(context_chunks),
                confidence=confidence,
                tokens_used=completion["usage"]["total_tokens"]
            )

            return result
            
        except Exception as e:
            logger.error("Failed to generate RAG answer", error=str(e))
            raise
    
    async def extract_key_facts(self, text: str) -> List[str]:
        """Extract key facts from text"""
        
        prompt = f"""Extract the key facts and statistics from the following text about population data. Return as a bulleted list.

Text:
{text}

Key Facts:"""
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        try:
            completion = await self.create_chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse the response into a list of facts
            content = completion["content"]
            facts = [fact.strip().lstrip("- ").lstrip("• ") for fact in content.split("\n") if fact.strip()]
            
            return facts
            
        except Exception as e:
            logger.error("Failed to extract key facts", error=str(e))
            return []
    
    @track_llm_call("validate_answer", tags=["openai", "validation", "quality"])
    async def validate_answer(self, question: str, answer: str, context: str) -> Dict[str, Any]:
        """Validate answer against context"""
        
        prompt = f"""Review the following answer to see if it's supported by the provided context.

Question: {question}
Answer: {answer}
Context: {context}

Evaluate the answer based on:
1. Accuracy: Does the answer match the context?
2. Completeness: Does it address all parts of the question?
3. Hallucination: Does it include information not in the context?

Provide your evaluation as a JSON object with these keys:
- "accuracy": (score 0-1)
- "completeness": (score 0-1)
- "hallucination": (score 0-1, 0 means no hallucination)
- "overall_score": (average of the above)
- "feedback": "specific feedback on the answer"
"""
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        try:
            completion = await self.create_chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=300
            )
            
            # Parse the JSON response (simple approach)
            content = completion["content"]
            
            # Extract scores using regex (basic implementation)
            import re
            
            scores = {}
            for metric in ["accuracy", "completeness", "hallucination", "overall_score"]:
                match = re.search(f'"{metric}":\s*(\d+\.?\d*)', content)
                if match:
                    scores[metric] = float(match.group(1))
                else:
                    scores[metric] = 0.0
            
            # Extract feedback
            feedback_match = re.search('"feedback":\s*"([^"]*)"', content)
            feedback = feedback_match.group(1) if feedback_match else "No feedback provided"
            
            # Log metadata to Opik
            log_llm_metadata({
                "question": question,
                "answer_preview": answer[:100] + "..." if len(answer) > 100 else answer,
                "context_preview": context[:200] + "..." if len(context) > 200 else context,
                "validation_scores": scores,
                "overall_score": scores.get("overall_score", 0.0)
            })

            return {
                "scores": scores,
                "feedback": feedback,
                "raw_response": content
            }
            
        except Exception as e:
            logger.error("Failed to validate answer", error=str(e))
            return {
                "scores": {"accuracy": 0.5, "completeness": 0.5, "hallucination": 0.5, "overall_score": 0.5},
                "feedback": f"Validation failed: {str(e)}",
                "raw_response": ""
            }