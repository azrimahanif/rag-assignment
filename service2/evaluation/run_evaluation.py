#!/usr/bin/env python3
"""
RAG Evaluation Engine - Automated evaluation of RAG system performance
Runs 15 evaluation queries and measures latency, retrieval hit-rate, and hallucination rate
"""

import json
import time
import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Tuple
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGEvaluator:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            "chat_webhook": "http://localhost:8000/api/v1/rag/query",
            "max_retries": 3,
            "timeout": 60,
            "queries_file": "evaluation/queries.json",
            "output_dir": "evaluation/results"
        }
        self.results = []
        
    async def send_query(self, query: str, session_id: str, conversation_id: int, message_id: int) -> Tuple[Dict, float]:
        """Send query to RAG system and measure response time"""
        start_time = time.time()

        try:
            # Use FastAPI RAG endpoint format
            payload = {
                "query": query,
                "max_results": 5,
                "similarity_threshold": 0.7
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config["chat_webhook"],
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config["timeout"])
                ) as response:
                    response_time = time.time() - start_time

                    if response.status == 200:
                        response_text = await response.text()

                        # Handle different response formats
                        try:
                            response_data = json.loads(response_text)

                            # Normalize response format
                            normalized_response = self._normalize_response_format(response_data)
                            return normalized_response, response_time

                        except json.JSONDecodeError:
                            # Handle raw text response
                            return {
                                "content": response_text,
                                "documents": [],
                                "raw_response": response_text
                            }, response_time
                    else:
                        error_text = await response.text()
                        logger.error(f"HTTP {response.status}: {error_text}")
                        return {"error": error_text, "status_code": response.status}, response_time

        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            logger.error(f"Query timeout after {self.config['timeout']}s")
            return {"error": "timeout", "message": "Query timed out"}, response_time
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Query failed: {str(e)}")
            return {"error": "exception", "message": str(e)}, response_time
    
    def _normalize_response_format(self, response_data: Dict) -> Dict:
        """Normalize different webhook response formats to standard format"""
        normalized = {
            "content": "",
            "documents": [],
            "raw_response": response_data
        }

        # Handle FastAPI RAG response format
        if isinstance(response_data, dict):
            normalized["content"] = response_data.get("answer", response_data.get("content", ""))

            # Convert sources to documents format
            sources = response_data.get("sources", [])
            if sources:
                normalized["documents"] = [
                    {"source": source, "text": f"Source: {source}"} for source in sources
                ]

            # Add metadata
            if "metadata" in response_data:
                normalized["metadata"] = response_data["metadata"]

        # Handle n8n array format (legacy)
        elif isinstance(response_data, list) and len(response_data) > 0:
            first_item = response_data[0]
            if isinstance(first_item, dict):
                normalized["content"] = first_item.get("output", first_item.get("content", ""))
                normalized["documents"] = first_item.get("documents", [])

        # Handle direct object format
        else:
            normalized["content"] = response_data.get("output", response_data.get("content", ""))
            normalized["documents"] = response_data.get("documents", [])
        
        return normalized
    
    def load_evaluation_queries(self) -> List[Dict]:
        """Load evaluation queries from JSON file"""
        try:
            with open(self.config["queries_file"], 'r') as f:
                data = json.load(f)
                queries = data.get("evaluation_queries", [])
            logger.info(f"Loaded {len(queries)} evaluation queries")
            return queries
        except FileNotFoundError:
            logger.error(f"Queries file not found: {self.config['queries_file']}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in queries file: {e}")
            return []
    
    def calculate_retrieval_hit_rate(self, response: Dict, expected_sources: List[str]) -> float:
        """Calculate retrieval hit-rate based on expected sources"""
        if "error" in response:
            return 0.0
            
        # Extract sources from response using enhanced logic
        retrieved_sources = []
        if "documents" in response:
            for doc in response.get("documents", []):
                source = "unknown"
                if isinstance(doc, dict):
                    # Try different possible source fields
                    source = doc.get("data_source") or doc.get("source") or doc.get("metadata", {}).get("data_source", "unknown")
                    
                    # Extract from text if still unknown
                    if source == "unknown" and "text" in doc:
                        text = doc.get("text", "")
                        if "Data source:" in text:
                            source = text.split("Data source:")[1].split("\n")[0].strip()
                        elif "state_parquet" in text:
                            source = "state_parquet"
                        elif "malaysia_api" in text:
                            source = "malaysia_api"
                
                retrieved_sources.append(source)
        
        # Calculate hit rate
        if not expected_sources:
            return 1.0 if not retrieved_sources else 0.0
            
        hits = sum(1 for expected in expected_sources if any(expected in retrieved for retrieved in retrieved_sources))
        return hits / len(expected_sources) if expected_sources else 0.0
    
    def detect_hallucinations(self, response: Dict, query: str, expected_key_facts: List[str]) -> Dict:
        """Detect potential hallucinations in response"""
        if "error" in response:
            return {"hallucination_detected": True, "reason": "error_response", "confidence": 1.0}
        
        response_content = response.get("content", "").lower()
        
        # Check for common hallucination patterns
        hallucination_indicators = [
            "i don't have information",
            "i don't know", 
            "information not available",
            "no data found",
            "cannot provide",
            "unable to answer",
            "i don't have access to",
            "i cannot find"
        ]
        
        hallucination_score = 0.0
        detected_issues = []
        
        # Check for uncertainty phrases
        for indicator in hallucination_indicators:
            if indicator in response_content:
                hallucination_score += 0.4
                detected_issues.append(f"uncertainty_phrase: {indicator}")
        
        # Check if response is too generic/vague (but be more lenient)
        if len(response_content) < 30 and not any(fact.lower() in response_content for fact in expected_key_facts):
            hallucination_score += 0.3
            detected_issues.append("too_generic_response")
        
        # Check for factual mismatches (be more lenient with partial matches)
        if expected_key_facts:
            facts_found = 0
            for fact in expected_key_facts:
                fact_lower = fact.lower()
                # Check for any part of the fact in response
                if any(keyword in response_content for keyword in fact_lower.split() if len(keyword) > 3):
                    facts_found += 1
            
            # If less than 30% of expected facts found, increase score
            if facts_found / len(expected_key_facts) < 0.3:
                hallucination_score += 0.2
                detected_issues.append(f"insufficient_expected_facts: {facts_found}/{len(expected_key_facts)}")
        
        # Bonus: Good responses with specific numbers and sources
        if any(char.isdigit() for char in response_content) and len(response_content) > 100:
            hallucination_score -= 0.2  # Reduce score for substantive responses
        
        if "source:" in response_content or "citation:" in response_content:
            hallucination_score -= 0.1  # Reduce score for cited responses
        
        return {
            "hallucination_detected": max(hallucination_score, 0) > 0.5,
            "confidence": max(min(hallucination_score, 1.0), 0),
            "issues": detected_issues
        }
    
    def extract_citations(self, response: Dict) -> List[Dict]:
        """Extract citations from response"""
        citations = []
        
        if "documents" in response:
            for doc in response.get("documents", []):
                # Extract source from document (multiple possible fields)
                source = "unknown"
                if isinstance(doc, dict):
                    # Try different possible source fields
                    source = doc.get("data_source") or doc.get("source") or doc.get("metadata", {}).get("data_source", "unknown")
                    
                    # Extract from text if still unknown
                    if source == "unknown" and "text" in doc:
                        text = doc.get("text", "")
                        if "Data source:" in text:
                            source = text.split("Data source:")[1].split("\n")[0].strip()
                        elif "state_parquet" in text:
                            source = "state_parquet"
                        elif "malaysia_api" in text:
                            source = "malaysia_api"
                
                citation = {
                    "source": source,
                    "chat_id": doc.get("chat_id", "unknown"),
                    "text_preview": self._create_text_preview(doc.get("text", ""))
                }
                citations.append(citation)
        
        return citations
    
    def _create_text_preview(self, text: str, max_length: int = 100) -> str:
        """Create a preview of document text"""
        if not text:
            return "No content available"
        
        # Clean up the text
        text = text.strip()
        if len(text) <= max_length:
            return text
        else:
            return text[:max_length] + "..."
    
    async def run_single_query_evaluation(self, query_data: Dict, query_index: int) -> Dict:
        """Run evaluation for a single query"""
        logger.info(f"Evaluating query {query_index + 1}: {query_data['query'][:50]}...")
        
        # Generate session and message IDs
        session_id = f"eval_session_{query_index}_{int(time.time())}"
        conversation_id = query_index + 1
        message_id = query_index + 1
        
        # Send query and measure response
        response, response_time = await self.send_query(
            query_data["query"], 
            session_id, 
            conversation_id, 
            message_id
        )
        
        # Calculate metrics
        retrieval_hit_rate = self.calculate_retrieval_hit_rate(
            response,
            query_data.get("expected_data_sources", [])
        )
        
        hallucination_analysis = self.detect_hallucinations(
            response,
            query_data["query"],
            query_data.get("expected_key_facts", [])
        )
        
        citations = self.extract_citations(response)
        
        # Compile results
        result = {
            "query_index": query_index,
            "query": query_data["query"],
            "query_category": query_data.get("category", "unknown"),
            "response_time": response_time,
            "response_content": response.get("content", "") if "error" not in response else "",
            "response_error": response.get("error", ""),
            "retrieval_hit_rate": retrieval_hit_rate,
            "hallucination_detected": hallucination_analysis["hallucination_detected"],
            "hallucination_confidence": hallucination_analysis["confidence"],
            "hallucination_issues": hallucination_analysis["issues"],
            "citations_count": len(citations),
            "citations": citations,
            "expected_key_facts": query_data.get("expected_key_facts", []),
            "expected_sources": query_data.get("expected_data_sources", []),
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
        
        logger.info(f"Query {query_index + 1} completed: {response_time:.2f}s, hit-rate: {retrieval_hit_rate:.2f}, hallucination: {hallucination_analysis['hallucination_detected']}")
        
        return result
    
    async def run_full_evaluation(self) -> Dict:
        """Run complete evaluation on all 15 queries"""
        logger.info("Starting RAG system evaluation...")
        
        queries = self.load_evaluation_queries()
        if not queries:
            return {"error": "Failed to load evaluation queries"}
        
        logger.info(f"Loaded {len(queries)} queries for evaluation")
        
        # Run evaluations concurrently
        tasks = []
        for i, query_data in enumerate(queries):
            task = self.run_single_query_evaluation(query_data, i)
            tasks.append(task)
        
        self.results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and calculate aggregate metrics
        successful_results = [r for r in self.results if not isinstance(r, Exception) and "error" not in r]
        
        if not successful_results:
            logger.error("No successful evaluation results")
            return {"error": "All evaluation queries failed"}
        
        # Calculate aggregate metrics
        response_times = [r["response_time"] for r in successful_results]
        hit_rates = [r["retrieval_hit_rate"] for r in successful_results]
        hallucination_rates = [r["hallucination_confidence"] for r in successful_results]
        
        aggregate_metrics = {
            "total_queries": len(queries),
            "successful_queries": len(successful_results),
            "failed_queries": len(queries) - len(successful_results),
            "latency_p50": np.percentile(response_times, 50),
            "latency_p95": np.percentile(response_times, 95),
            "latency_mean": np.mean(response_times),
            "retrieval_hit_rate_mean": np.mean(hit_rates),
            "retrieval_hit_rate_std": np.std(hit_rates),
            "hallucination_rate_mean": np.mean(hallucination_rates),
            "hallucination_rate_std": np.std(hallucination_rates),
            "total_citations": sum(r["citations_count"] for r in successful_results),
            "avg_citations_per_query": np.mean([r["citations_count"] for r in successful_results])
        }
        
        # Category-based analysis
        category_analysis = {}
        for category in set(r["query_category"] for r in successful_results):
            category_results = [r for r in successful_results if r["query_category"] == category]
            category_analysis[category] = {
                "count": len(category_results),
                "avg_latency": np.mean([r["response_time"] for r in category_results]),
                "avg_hit_rate": np.mean([r["retrieval_hit_rate"] for r in category_results]),
                "avg_hallucination_rate": np.mean([r["hallucination_confidence"] for r in category_results])
            }
        
        evaluation_summary = {
            "evaluation_timestamp": datetime.now().isoformat(),
            "aggregate_metrics": aggregate_metrics,
            "category_analysis": category_analysis,
            "detailed_results": successful_results,
            "failed_queries": [r for r in self.results if isinstance(r, Exception) or "error" in r]
        }
        
        logger.info(f"Evaluation completed successfully: {len(successful_results)}/{len(queries)} queries succeeded")
        logger.info(f"Latency P50: {aggregate_metrics['latency_p50']:.2f}s, P95: {aggregate_metrics['latency_p95']:.2f}s")
        logger.info(f"Retrieval hit-rate: {aggregate_metrics['retrieval_hit_rate_mean']:.2f}")
        logger.info(f"Hallucination rate: {aggregate_metrics['hallucination_rate_mean']:.2f}")
        
        return evaluation_summary
    
    def save_results(self, results: Dict, filename: str = None):
        """Save evaluation results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"evaluation_results_{timestamp}.json"
        
        output_path = Path(self.config["output_dir"]) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Results saved to {output_path}")
        return str(output_path)
    
    def generate_csv_report(self, results: Dict, filename: str = None):
        """Generate CSV report of evaluation results"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"evaluation_report_{timestamp}.csv"
        
        output_path = Path(self.config["output_dir"]) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create DataFrame from detailed results
        df_data = []
        for result in results.get("detailed_results", []):
            df_data.append({
                "query_index": result["query_index"],
                "query": result["query"],
                "category": result["query_category"],
                "response_time": result["response_time"],
                "retrieval_hit_rate": result["retrieval_hit_rate"],
                "hallucination_detected": result["hallucination_detected"],
                "hallucination_confidence": result["hallucination_confidence"],
                "citations_count": result["citations_count"],
                "error": result.get("response_error", "")
            })
        
        df = pd.DataFrame(df_data)
        df.to_csv(output_path, index=False)
        
        logger.info(f"CSV report saved to {output_path}")
        return str(output_path)

async def main():
    """Main evaluation execution"""
    evaluator = RAGEvaluator()
    
    logger.info("Starting RAG system evaluation...")
    
    # Run full evaluation
    results = await evaluator.run_full_evaluation()
    
    if "error" in results:
        logger.error(f"Evaluation failed: {results['error']}")
        return
    
    # Save results
    json_file = evaluator.save_results(results)
    csv_file = evaluator.generate_csv_report(results)
    
    # Print summary
    metrics = results["aggregate_metrics"]
    print("\n" + "="*60)
    print("RAG SYSTEM EVALUATION RESULTS")
    print("="*60)
    print(f"Total Queries: {metrics['total_queries']}")
    print(f"Successful: {metrics['successful_queries']}")
    print(f"Failed: {metrics['failed_queries']}")
    print(f"Latency P50: {metrics['latency_p50']:.2f}s")
    print(f"Latency P95: {metrics['latency_p95']:.2f}s")
    print(f"Retrieval Hit Rate: {metrics['retrieval_hit_rate_mean']:.2f}")
    print(f"Hallucination Rate: {metrics['hallucination_rate_mean']:.2f}")
    print(f"Avg Citations per Query: {metrics['avg_citations_per_query']:.1f}")
    print("="*60)
    print(f"Results saved to: {json_file}")
    print(f"CSV report: {csv_file}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())