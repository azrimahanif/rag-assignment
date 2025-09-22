#!/usr/bin/env python3
"""
Metrics Calculator for RAG Evaluation System
Provides detailed metrics calculation and analysis functions
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class RAGMetricsCalculator:
    """Advanced metrics calculation for RAG system evaluation"""
    
    def __init__(self):
        self.metrics_history = []
    
    def calculate_latency_metrics(self, response_times: List[float]) -> Dict[str, float]:
        """Calculate comprehensive latency metrics"""
        if not response_times:
            return {"error": "No response times provided"}
        
        sorted_times = sorted(response_times)
        n = len(sorted_times)
        
        metrics = {
            "count": n,
            "mean": np.mean(response_times),
            "median": np.median(response_times),
            "std": np.std(response_times),
            "min": min(response_times),
            "max": max(response_times),
            "p25": np.percentile(response_times, 25),
            "p50": np.percentile(response_times, 50),
            "p75": np.percentile(response_times, 75),
            "p90": np.percentile(response_times, 90),
            "p95": np.percentile(response_times, 95),
            "p99": np.percentile(response_times, 99),
            "range": max(response_times) - min(response_times)
        }
        
        return metrics
    
    def calculate_retrieval_metrics(self, hit_rates: List[float]) -> Dict[str, float]:
        """Calculate comprehensive retrieval metrics"""
        if not hit_rates:
            return {"error": "No hit rates provided"}
        
        metrics = {
            "count": len(hit_rates),
            "mean": np.mean(hit_rates),
            "median": np.median(hit_rates),
            "std": np.std(hit_rates),
            "min": min(hit_rates),
            "max": max(hit_rates),
            "success_rate": sum(1 for rate in hit_rates if rate >= 0.8) / len(hit_rates),
            "partial_success_rate": sum(1 for rate in hit_rates if 0.5 <= rate < 0.8) / len(hit_rates),
            "failure_rate": sum(1 for rate in hit_rates if rate < 0.5) / len(hit_rates)
        }
        
        return metrics
    
    def calculate_hallucination_metrics(self, hallucination_scores: List[float]) -> Dict[str, float]:
        """Calculate comprehensive hallucination metrics"""
        if not hallucination_scores:
            return {"error": "No hallucination scores provided"}
        
        metrics = {
            "count": len(hallucination_scores),
            "mean": np.mean(hallucination_scores),
            "median": np.median(hallucination_scores),
            "std": np.std(hallucination_scores),
            "min": min(hallucination_scores),
            "max": max(hallucination_scores),
            "critical_hallucination_rate": sum(1 for score in hallucination_scores if score >= 0.8) / len(hallucination_scores),
            "moderate_hallucination_rate": sum(1 for score in hallucination_scores if 0.5 <= score < 0.8) / len(hallucination_scores),
            "low_hallucination_rate": sum(1 for score in hallucination_scores if score < 0.5) / len(hallucination_scores)
        }
        
        return metrics
    
    def calculate_citation_metrics(self, citation_counts: List[int]) -> Dict[str, float]:
        """Calculate citation quality metrics"""
        if not citation_counts:
            return {"error": "No citation counts provided"}
        
        metrics = {
            "count": len(citation_counts),
            "mean": np.mean(citation_counts),
            "median": np.median(citation_counts),
            "std": np.std(citation_counts),
            "min": min(citation_counts),
            "max": max(citation_counts),
            "zero_citation_rate": sum(1 for count in citation_counts if count == 0) / len(citation_counts),
            "low_citation_rate": sum(1 for count in citation_counts if count == 1) / len(citation_counts),
            "good_citation_rate": sum(1 for count in citation_counts if count >= 2) / len(citation_counts)
        }
        
        return metrics
    
    def calculate_category_performance(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate performance metrics by query category"""
        if not results:
            return {"error": "No results provided"}
        
        categories = set(r.get("query_category", "unknown") for r in results)
        category_metrics = {}
        
        for category in categories:
            category_results = [r for r in results if r.get("query_category") == category]
            
            if not category_results:
                continue
            
            # Extract metrics for this category
            response_times = [r.get("response_time", 0) for r in category_results]
            hit_rates = [r.get("retrieval_hit_rate", 0) for r in category_results]
            hallucination_scores = [r.get("hallucination_confidence", 0) for r in category_results]
            citation_counts = [r.get("citations_count", 0) for r in category_results]
            
            category_metrics[category] = {
                "count": len(category_results),
                "latency": self.calculate_latency_metrics(response_times),
                "retrieval": self.calculate_retrieval_metrics(hit_rates),
                "hallucination": self.calculate_hallucination_metrics(hallucination_scores),
                "citations": self.calculate_citation_metrics(citation_counts),
                "queries": [r.get("query", "") for r in category_results]
            }
        
        return category_metrics
    
    def calculate_quality_score(self, results: List[Dict]) -> Dict[str, float]:
        """Calculate overall quality score based on multiple metrics"""
        if not results:
            return {"error": "No results provided"}
        
        # Extract individual metrics
        response_times = [r.get("response_time", float('inf')) for r in results]
        hit_rates = [r.get("retrieval_hit_rate", 0) for r in results]
        hallucination_scores = [r.get("hallucination_confidence", 1) for r in results]
        citation_counts = [r.get("citations_count", 0) for r in results]
        
        # Calculate individual component scores (0-1 scale)
        latency_score = 1.0 - min(np.mean(response_times) / 30.0, 1.0)  # Normalize to 30s max
        retrieval_score = np.mean(hit_rates)
        hallucination_score = 1.0 - np.mean(hallucination_scores)
        citation_score = min(np.mean(citation_counts) / 3.0, 1.0)  # Normalize to 3 citations max
        
        # Calculate weighted overall score
        overall_score = (
            latency_score * 0.2 +      # 20% weight for speed
            retrieval_score * 0.4 +    # 40% weight for retrieval accuracy
            hallucination_score * 0.3 + # 30% weight for factual accuracy
            citation_score * 0.1       # 10% weight for source citations
        )
        
        quality_metrics = {
            "overall_score": overall_score,
            "latency_score": latency_score,
            "retrieval_score": retrieval_score,
            "hallucination_score": hallucination_score,
            "citation_score": citation_score,
            "performance_grade": self._get_performance_grade(overall_score)
        }
        
        return quality_metrics
    
    def _get_performance_grade(self, score: float) -> str:
        """Convert numerical score to letter grade"""
        if score >= 0.9:
            return "A+"
        elif score >= 0.8:
            return "A"
        elif score >= 0.7:
            return "B"
        elif score >= 0.6:
            return "C"
        elif score >= 0.5:
            return "D"
        else:
            return "F"
    
    def analyze_trends(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        if len(historical_data) < 2:
            return {"error": "Insufficient historical data for trend analysis"}
        
        # Extract timestamps and metrics
        timestamps = []
        latencies = []
        hit_rates = []
        hallucination_scores = []
        
        for evaluation in historical_data:
            if "evaluation_timestamp" in evaluation and "aggregate_metrics" in evaluation:
                timestamps.append(datetime.fromisoformat(evaluation["evaluation_timestamp"]))
                metrics = evaluation["aggregate_metrics"]
                latencies.append(metrics.get("latency_mean", 0))
                hit_rates.append(metrics.get("retrieval_hit_rate_mean", 0))
                hallucination_scores.append(metrics.get("hallucination_rate_mean", 0))
        
        if len(timestamps) < 2:
            return {"error": "No valid timestamped evaluations found"}
        
        # Calculate trends
        time_diffs = [(timestamps[i] - timestamps[0]).total_seconds() / 3600 for i in range(len(timestamps))]  # hours
        
        trend_analysis = {
            "time_span_hours": max(time_diffs),
            "evaluations_count": len(timestamps),
            "latency_trend": self._calculate_trend(time_diffs, latencies),
            "hit_rate_trend": self._calculate_trend(time_diffs, hit_rates),
            "hallucination_trend": self._calculate_trend(time_diffs, hallucination_scores),
            "stability_analysis": self._analyze_stability(latencies, hit_rates, hallucination_scores)
        }
        
        return trend_analysis
    
    def _calculate_trend(self, x_values: List[float], y_values: List[float]) -> Dict[str, float]:
        """Calculate linear trend slope and correlation"""
        if len(x_values) < 2 or len(y_values) < 2:
            return {"slope": 0, "correlation": 0}
        
        # Calculate linear regression slope
        x_mean = np.mean(x_values)
        y_mean = np.mean(y_values)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return {"slope": 0, "correlation": 0}
        
        slope = numerator / denominator
        
        # Calculate correlation coefficient
        x_std = np.std(x_values)
        y_std = np.std(y_values)
        
        if x_std == 0 or y_std == 0:
            correlation = 0
        else:
            correlation = numerator / (len(x_values) * x_std * y_std)
        
        return {
            "slope": slope,
            "correlation": correlation,
            "direction": "improving" if (slope > 0 and y_values[0] < y_values[-1]) or (slope < 0 and y_values[0] > y_values[-1]) else "declining"
        }
    
    def _analyze_stability(self, latencies: List[float], hit_rates: List[float], hallucination_scores: List[float]) -> Dict[str, float]:
        """Analyze system stability metrics"""
        stability_metrics = {
            "latency_cv": np.std(latencies) / np.mean(latencies) if np.mean(latencies) > 0 else 0,
            "hit_rate_cv": np.std(hit_rates) / np.mean(hit_rates) if np.mean(hit_rates) > 0 else 0,
            "hallucination_cv": np.std(hallucination_scores) / np.mean(hallucination_scores) if np.mean(hallucination_scores) > 0 else 0,
            "overall_stability_score": 0
        }
        
        # Calculate overall stability (lower CV = more stable)
        latency_stability = max(0, 1 - stability_metrics["latency_cv"])
        hit_rate_stability = max(0, 1 - stability_metrics["hit_rate_cv"])
        hallucination_stability = max(0, 1 - stability_metrics["hallucination_cv"])
        
        stability_metrics["overall_stability_score"] = (latency_stability + hit_rate_stability + hallucination_stability) / 3
        
        return stability_metrics
    
    def generate_comprehensive_report(self, evaluation_results: Dict) -> Dict[str, Any]:
        """Generate comprehensive evaluation report"""
        detailed_results = evaluation_results.get("detailed_results", [])
        
        if not detailed_results:
            return {"error": "No detailed results found"}
        
        # Calculate all metrics
        response_times = [r.get("response_time", 0) for r in detailed_results]
        hit_rates = [r.get("retrieval_hit_rate", 0) for r in detailed_results]
        hallucination_scores = [r.get("hallucination_confidence", 0) for r in detailed_results]
        citation_counts = [r.get("citations_count", 0) for r in detailed_results]
        
        comprehensive_report = {
            "report_timestamp": datetime.now().isoformat(),
            "evaluation_summary": {
                "total_queries": len(detailed_results),
                "successful_queries": len([r for r in detailed_results if not r.get("response_error")]),
                "failed_queries": len([r for r in detailed_results if r.get("response_error")])
            },
            "latency_metrics": self.calculate_latency_metrics(response_times),
            "retrieval_metrics": self.calculate_retrieval_metrics(hit_rates),
            "hallucination_metrics": self.calculate_hallucination_metrics(hallucination_scores),
            "citation_metrics": self.calculate_citation_metrics(citation_counts),
            "category_performance": self.calculate_category_performance(detailed_results),
            "quality_score": self.calculate_quality_score(detailed_results),
            "recommendations": self._generate_recommendations(detailed_results)
        }
        
        return comprehensive_report
    
    def _generate_recommendations(self, results: List[Dict]) -> List[str]:
        """Generate improvement recommendations based on results"""
        recommendations = []
        
        # Analyze latency
        response_times = [r.get("response_time", 0) for r in results]
        if np.mean(response_times) > 10:
            recommendations.append("Consider optimizing response time - current average exceeds 10 seconds")
        
        # Analyze retrieval
        hit_rates = [r.get("retrieval_hit_rate", 0) for r in results]
        if np.mean(hit_rates) < 0.7:
            recommendations.append("Retrieval accuracy below 70% - consider improving search algorithms or data indexing")
        
        # Analyze hallucinations
        hallucination_scores = [r.get("hallucination_confidence", 0) for r in results]
        if np.mean(hallucination_scores) > 0.3:
            recommendations.append("High hallucination rate detected - consider improving fact-checking and response validation")
        
        # Analyze citations
        citation_counts = [r.get("citations_count", 0) for r in results]
        if np.mean(citation_counts) < 1:
            recommendations.append("Low citation rate - ensure responses include proper source citations")
        
        # Category-specific recommendations
        category_performance = self.calculate_category_performance(results)
        for category, metrics in category_performance.items():
            if metrics["retrieval"]["mean"] < 0.6:
                recommendations.append(f"Consider improving {category} query handling - retrieval accuracy is low")
        
        if not recommendations:
            recommendations.append("System performance is good - continue monitoring")
        
        return recommendations

# Utility functions for data processing
def load_historical_data(results_dir: str) -> List[Dict]:
    """Load historical evaluation data from JSON files"""
    results_path = Path(results_dir)
    historical_data = []
    
    if not results_path.exists():
        return historical_data
    
    for file_path in results_path.glob("evaluation_results_*.json"):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                historical_data.append(data)
        except Exception as e:
            logger.warning(f"Failed to load {file_path}: {e}")
    
    return sorted(historical_data, key=lambda x: x.get("evaluation_timestamp", ""))

def save_metrics_report(report: Dict, filename: str):
    """Save metrics report to JSON file"""
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    logger.info(f"Metrics report saved to {filename}")

if __name__ == "__main__":
    # Example usage
    calculator = RAGMetricsCalculator()
    
    # Example data
    sample_results = [
        {"query_category": "simple_factual", "response_time": 5.2, "retrieval_hit_rate": 0.9, "hallucination_confidence": 0.1, "citations_count": 2},
        {"query_category": "complex_multi_step", "response_time": 12.5, "retrieval_hit_rate": 0.6, "hallucination_confidence": 0.4, "citations_count": 1},
    ]
    
    quality_score = calculator.calculate_quality_score(sample_results)
    print("Quality Score:", quality_score)