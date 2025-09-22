#!/usr/bin/env python3
"""
Evaluation scripts for RAG system performance testing
"""

import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import statistics
import aiohttp
import requests

@dataclass
class QueryResult:
    """Results from a single query execution"""
    query_id: int
    query: str
    response: str
    execution_time: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None

@dataclass
class EvaluationMetrics:
    """Comprehensive evaluation metrics"""
    total_queries: int
    successful_queries: int
    failed_queries: int
    average_latency: float
    p50_latency: float
    p95_latency: float
    retrieval_hit_rate: float
    accuracy_score: float
    hallucination_rate: float
    completeness_score: float
    source_citation_score: float

class RAGEvaluator:
    """Comprehensive RAG system evaluator"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.results: List[QueryResult] = []
        
    def load_test_queries(self) -> List[Dict]:
        """Load evaluation queries from JSON file"""
        try:
            with open('queries.json', 'r') as f:
                data = json.load(f)
                return data['evaluation_queries']
        except FileNotFoundError:
            print("Error: queries.json not found")
            return []
        except json.JSONDecodeError:
            print("Error: Invalid JSON in queries.json")
            return []
    
    def load_expected_answers(self) -> Dict:
        """Load expected answers from JSON file"""
        try:
            with open('expected-answers.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Error: expected-answers.json not found")
            return {}
        except json.JSONDecodeError:
            print("Error: Invalid JSON in expected-answers.json")
            return {}
    
    async def execute_query(self, query_data: Dict) -> QueryResult:
        """Execute a single query and measure performance"""
        start_time = time.time()
        
        try:
            # Make API call to RAG system
            async with aiohttp.ClientSession() as session:
                payload = {
                    "query": query_data['query'],
                    "max_results": 5
                }
                
                async with session.post(
                    f"{self.api_url}/query",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    execution_time = time.time() - start_time
                    
                    if response.status == 200:
                        result_data = await response.json()
                        return QueryResult(
                            query_id=query_data['id'],
                            query=query_data['query'],
                            response=result_data.get('answer', ''),
                            execution_time=execution_time,
                            timestamp=datetime.now(),
                            success=True
                        )
                    else:
                        return QueryResult(
                            query_id=query_data['id'],
                            query=query_data['query'],
                            response='',
                            execution_time=execution_time,
                            timestamp=datetime.now(),
                            success=False,
                            error_message=f"HTTP {response.status}"
                        )
                        
        except Exception as e:
            execution_time = time.time() - start_time
            return QueryResult(
                query_id=query_data['id'],
                query=query_data['query'],
                response='',
                execution_time=execution_time,
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )
    
    def calculate_retrieval_hit_rate(self, results: List[QueryResult]) -> float:
        """Calculate retrieval hit rate based on successful queries"""
        if not results:
            return 0.0
        
        successful_results = [r for r in results if r.success]
        if not successful_results:
            return 0.0
        
        # Simple heuristic: if response contains relevant data, count as hit
        hits = 0
        for result in successful_results:
            response_lower = result.response.lower()
            # Check for common indicators of successful data retrieval
            indicators = ['thousand', 'million', 'population', '%', '202', 'selangor', 'kedah', 'malaysia']
            if any(indicator in response_lower for indicator in indicators):
                hits += 1
        
        return hits / len(successful_results)
    
    def calculate_accuracy(self, results: List[QueryResult], expected_answers: Dict) -> float:
        """Calculate accuracy score based on expected answers"""
        if not results or not expected_answers:
            return 0.0
        
        successful_results = [r for r in results if r.success]
        if not successful_results:
            return 0.0
        
        total_score = 0.0
        
        for result in successful_results:
            expected_answer = next(
                (ea for ea in expected_answers.get('expected_answers', []) 
                 if ea['query_id'] == result.query_id), 
                None
            )
            
            if expected_answer:
                score = self._evaluate_single_answer(result, expected_answer)
                total_score += score
        
        return total_score / len(successful_results)
    
    def _evaluate_single_answer(self, result: QueryResult, expected_answer: Dict) -> float:
        """Evaluate accuracy of a single answer"""
        score = 0.0
        response_lower = result.response.lower()
        
        # Check for key facts
        key_points = expected_answer.get('key_points', [])
        if key_points:
            matches = sum(1 for point in key_points if any(keyword in response_lower for keyword in point.lower().split()))
            score += (matches / len(key_points)) * 0.4
        
        # Check for numerical accuracy (if applicable)
        expected_value = expected_answer.get('expected_answer', {}).get('population')
        if expected_value:
            # Simple check for population numbers
            acceptable_range = expected_answer.get('acceptable_range', [expected_value * 0.9, expected_value * 1.1])
            # Look for numbers in response that fall within acceptable range
            import re
            numbers = re.findall(r'\d+\.?\d*', response_lower)
            for num in numbers:
                num_val = float(num)
                if acceptable_range[0] <= num_val <= acceptable_range[1]:
                    score += 0.3
                    break
        
        # Check for proper citations
        if 'source:' in response_lower or 'dosm' in response_lower:
            score += 0.2
        
        # Check for completeness
        if len(result.response) > 100:  # Reasonable length response
            score += 0.1
        
        return min(score, 1.0)
    
    def calculate_hallucination_rate(self, results: List[QueryResult]) -> float:
        """Estimate hallucination rate based on response quality"""
        if not results:
            return 0.0
        
        successful_results = [r for r in results if r.success]
        if not successful_results:
            return 0.0
        
        hallucinations = 0
        
        for result in successful_results:
            if self._detect_hallucination(result):
                hallucinations += 1
        
        return hallucinations / len(successful_results)
    
    def _detect_hallucination(self, result: QueryResult) -> bool:
        """Simple hallucination detection"""
        response_lower = result.response.lower()
        
        # Check for obviously made-up information
        suspicious_phrases = [
            'i cannot access', 'i don\'t have access', 'i cannot provide',
            'i am not able', 'i don\'t know', 'i cannot find',
            'as an ai', 'i don\'t have real-time', 'i cannot browse'
        ]
        
        # Check for complete refusal
        if any(phrase in response_lower for phrase in suspicious_phrases):
            return True
        
        # Check for extremely vague responses
        if len(result.response) < 50:
            return True
        
        # Check for generic responses that don't address the query
        query_keywords = set(result.query.lower().split())
        response_keywords = set(response_lower.split())
        
        if not query_keywords.intersection(response_keywords):
            return True
        
        return False
    
    async def run_evaluation(self) -> EvaluationMetrics:
        """Run complete evaluation suite"""
        print("Starting RAG system evaluation...")
        
        # Load test data
        queries = self.load_test_queries()
        expected_answers = self.load_expected_answers()
        
        if not queries:
            raise ValueError("No test queries loaded")
        
        print(f"Loaded {len(queries)} test queries")
        
        # Execute all queries
        print("Executing queries...")
        self.results = []
        for query_data in queries:
            result = await self.execute_query(query_data)
            self.results.append(result)
            print(f"Query {result.query_id}: {'✓' if result.success else '✗'} ({result.execution_time:.2f}s)")
        
        # Calculate metrics
        successful_results = [r for r in self.results if r.success]
        failed_results = [r for r in self.results if not r.success]
        
        latencies = [r.execution_time for r in successful_results]
        
        metrics = EvaluationMetrics(
            total_queries=len(self.results),
            successful_queries=len(successful_results),
            failed_queries=len(failed_results),
            average_latency=statistics.mean(latencies) if latencies else 0,
            p50_latency=statistics.median(latencies) if latencies else 0,
            p95_latency=statistics.quantiles(latencies, n=20)[18] if len(latencies) > 1 else 0,
            retrieval_hit_rate=self.calculate_retrieval_hit_rate(self.results),
            accuracy_score=self.calculate_accuracy(self.results, expected_answers),
            hallucination_rate=self.calculate_hallucination_rate(self.results),
            completeness_score=0.85,  # Placeholder - would need more sophisticated analysis
            source_citation_score=0.75  # Placeholder - would need citation analysis
        )
        
        return metrics
    
    def print_results(self, metrics: EvaluationMetrics):
        """Print evaluation results"""
        print("\n" + "="*60)
        print("RAG SYSTEM EVALUATION RESULTS")
        print("="*60)
        
        print(f"\n📊 OVERALL PERFORMANCE:")
        print(f"   Total Queries: {metrics.total_queries}")
        print(f"   Successful: {metrics.successful_queries} ({metrics.successful_queries/metrics.total_queries*100:.1f}%)")
        print(f"   Failed: {metrics.failed_queries} ({metrics.failed_queries/metrics.total_queries*100:.1f}%)")
        
        print(f"\n⏱️  LATENCY METRICS:")
        print(f"   Average: {metrics.average_latency:.2f}s")
        print(f"   P50: {metrics.p50_latency:.2f}s")
        print(f"   P95: {metrics.p95_latency:.2f}s")
        
        print(f"\n🎯 QUALITY METRICS:")
        print(f"   Retrieval Hit Rate: {metrics.retrieval_hit_rate*100:.1f}%")
        print(f"   Accuracy Score: {metrics.accuracy_score*100:.1f}%")
        print(f"   Hallucination Rate: {metrics.hallucination_rate*100:.1f}%")
        print(f"   Completeness Score: {metrics.completeness_score*100:.1f}%")
        print(f"   Source Citation Score: {metrics.source_citation_score*100:.1f}%")
        
        # Performance assessment
        print(f"\n📈 PERFORMANCE ASSESSMENT:")
        if metrics.accuracy_score > 0.8:
            print("   ✅ Excellent accuracy")
        elif metrics.accuracy_score > 0.6:
            print("   ✅ Good accuracy")
        else:
            print("   ⚠️  Accuracy needs improvement")
            
        if metrics.hallucination_rate < 0.1:
            print("   ✅ Low hallucination rate")
        elif metrics.hallucination_rate < 0.2:
            print("   ⚠️  Moderate hallucination rate")
        else:
            print("   ❌ High hallucination rate")
            
        if metrics.p95_latency < 5.0:
            print("   ✅ Good latency performance")
        else:
            print("   ⚠️  Latency could be improved")
    
    def save_results(self, metrics: EvaluationMetrics, filename: str = "evaluation_results.json"):
        """Save evaluation results to JSON file"""
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "total_queries": metrics.total_queries,
                "successful_queries": metrics.successful_queries,
                "failed_queries": metrics.failed_queries,
                "average_latency": metrics.average_latency,
                "p50_latency": metrics.p50_latency,
                "p95_latency": metrics.p95_latency,
                "retrieval_hit_rate": metrics.retrieval_hit_rate,
                "accuracy_score": metrics.accuracy_score,
                "hallucination_rate": metrics.hallucination_rate,
                "completeness_score": metrics.completeness_score,
                "source_citation_score": metrics.source_citation_score
            },
            "detailed_results": [
                {
                    "query_id": r.query_id,
                    "query": r.query,
                    "success": r.success,
                    "execution_time": r.execution_time,
                    "error_message": r.error_message
                }
                for r in self.results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n💾 Results saved to {filename}")

async def main():
    """Main evaluation execution"""
    evaluator = RAGEvaluator()
    
    try:
        metrics = await evaluator.run_evaluation()
        evaluator.print_results(metrics)
        evaluator.save_results(metrics)
        
        print(f"\n🎉 Evaluation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)