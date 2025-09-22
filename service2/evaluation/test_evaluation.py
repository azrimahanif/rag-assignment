#!/usr/bin/env python3
"""
Test script for RAG evaluation system
Verifies that all evaluation components work correctly
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the evaluation directory to Python path
sys.path.append(str(Path(__file__).parent))

from run_evaluation import RAGEvaluator
from metrics_calculator import RAGMetricsCalculator

async def test_evaluation_system():
    """Test the evaluation system with sample data"""
    print("Testing RAG Evaluation System...")
    print("=" * 50)
    
    # Test 1: Load queries
    print("1. Testing query loading...")
    evaluator = RAGEvaluator()
    queries = evaluator.load_evaluation_queries()
    
    if queries:
        print(f"✅ Successfully loaded {len(queries)} queries")
        print(f"   Categories: {set(q.get('category', 'unknown') for q in queries)}")
    else:
        print("❌ Failed to load queries")
        return False
    
    # Test 2: Metrics calculator
    print("\n2. Testing metrics calculator...")
    calculator = RAGMetricsCalculator()
    
    # Test latency metrics
    sample_times = [2.5, 3.1, 1.8, 4.2, 2.9]
    latency_metrics = calculator.calculate_latency_metrics(sample_times)
    if "error" not in latency_metrics:
        print("✅ Latency metrics calculation works")
        print(f"   P50: {latency_metrics['p50']:.2f}s, P95: {latency_metrics['p95']:.2f}s")
    else:
        print("❌ Latency metrics calculation failed")
        return False
    
    # Test 3: Quality score calculation
    print("\n3. Testing quality score calculation...")
    sample_results = [
        {
            "query_category": "simple_factual",
            "response_time": 3.2,
            "retrieval_hit_rate": 0.85,
            "hallucination_confidence": 0.15,
            "citations_count": 2
        },
        {
            "query_category": "complex_multi_step",
            "response_time": 8.7,
            "retrieval_hit_rate": 0.65,
            "hallucination_confidence": 0.35,
            "citations_count": 1
        }
    ]
    
    quality_score = calculator.calculate_quality_score(sample_results)
    if "error" not in quality_score:
        print("✅ Quality score calculation works")
        print(f"   Overall Score: {quality_score['overall_score']:.3f} ({quality_score['performance_grade']})")
    else:
        print("❌ Quality score calculation failed")
        return False
    
    # Test 4: Configuration
    print("\n4. Testing evaluator configuration...")
    config = evaluator.config
    expected_keys = ["chat_webhook", "max_retries", "timeout", "queries_file", "output_dir"]
    
    missing_keys = [key for key in expected_keys if key not in config]
    if not missing_keys:
        print("✅ Evaluator configuration is complete")
        print(f"   Webhook URL: {config['chat_webhook']}")
        print(f"   Timeout: {config['timeout']}s")
    else:
        print(f"❌ Missing configuration keys: {missing_keys}")
        return False
    
    # Test 5: Directory structure
    print("\n5. Testing directory structure...")
    required_paths = [
        Path("evaluation/queries.json"),
        Path("evaluation/results")
    ]
    
    missing_paths = [path for path in required_paths if not path.exists()]
    if not missing_paths:
        print("✅ Required directories and files exist")
    else:
        print(f"❌ Missing paths: {missing_paths}")
        # Create results directory if missing
        Path("evaluation/results").mkdir(parents=True, exist_ok=True)
        print("   Created missing results directory")
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! Evaluation system is ready.")
    print("\nTo run full evaluation:")
    print("  python evaluation/run_evaluation.py")
    print("\nTo test with single query:")
    print("  python evaluation/test_single_query.py")
    
    return True

def test_sample_calculation():
    """Test metrics calculation with sample data"""
    print("\nSample Metrics Calculation:")
    print("-" * 30)
    
    calculator = RAGMetricsCalculator()
    
    # Sample data representing typical RAG system performance
    response_times = [2.1, 3.5, 1.8, 4.2, 2.9, 3.7, 2.3, 5.1, 2.8, 3.2]
    hit_rates = [0.9, 0.8, 0.95, 0.7, 0.85, 0.75, 0.9, 0.65, 0.88, 0.82]
    hallucination_scores = [0.1, 0.2, 0.05, 0.35, 0.15, 0.25, 0.12, 0.4, 0.18, 0.22]
    citation_counts = [2, 1, 3, 1, 2, 1, 2, 0, 2, 1]
    
    # Calculate comprehensive metrics
    latency_metrics = calculator.calculate_latency_metrics(response_times)
    retrieval_metrics = calculator.calculate_retrieval_metrics(hit_rates)
    hallucination_metrics = calculator.calculate_hallucination_metrics(hallucination_scores)
    citation_metrics = calculator.calculate_citation_metrics(citation_counts)
    
    print(f"Latency:")
    print(f"  P50: {latency_metrics['p50']:.2f}s")
    print(f"  P95: {latency_metrics['p95']:.2f}s")
    print(f"  Mean: {latency_metrics['mean']:.2f}s")
    
    print(f"\nRetrieval:")
    print(f"  Hit Rate: {retrieval_metrics['mean']:.2f}")
    print(f"  Success Rate: {retrieval_metrics['success_rate']:.2f}")
    
    print(f"\nHallucination:")
    print(f"  Rate: {hallucination_metrics['mean']:.2f}")
    print(f"  Critical: {hallucination_metrics['critical_hallucination_rate']:.2f}")
    
    print(f"\nCitations:")
    print(f"  Average: {citation_metrics['mean']:.1f}")
    print(f"  Zero Rate: {citation_metrics['zero_citation_rate']:.2f}")

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_evaluation_system())
    
    if success:
        # Show sample calculation
        test_sample_calculation()
    else:
        print("\n❌ Evaluation system tests failed!")
        sys.exit(1)