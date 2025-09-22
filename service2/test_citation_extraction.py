#!/usr/bin/env python3
"""
Test citation extraction from sample webhook response
"""

import sys
sys.path.append('evaluation')

from run_evaluation import RAGEvaluator

def test_citation_extraction():
    """Test citation extraction with sample data"""
    evaluator = RAGEvaluator()
    
    # Sample response like your actual webhook output
    sample_response = {
        "content": "Here's a comparison of the population between Kedah and Selangor...",
        "documents": [
            {
                "chat_id": "test_session_2",
                "text": "Population data for Selangor in 2015.\n    \nTotal population: 6,178.0 thousand people.\n\nGender Breakdown:\n- Both: 6,178.0k (100.0%)\n\nData source: state_parquet\nCoverage: 399 demographic data points"
            },
            {
                "chat_id": "test_session_2", 
                "text": "Population data for Kedah in 2014.\n    \nTotal population: 2,062.7 thousand people.\n\nGender Breakdown:\n- Both: 2,062.7k (100.0%)\n\nData source: state_parquet\nCoverage: 399 demographic data points"
            }
        ]
    }
    
    print("Testing Citation Extraction")
    print("="*50)
    
    citations = evaluator.extract_citations(sample_response)
    
    print(f"Extracted {len(citations)} citations:")
    for i, citation in enumerate(citations):
        print(f"\nCitation {i+1}:")
        print(f"  Source: {citation['source']}")
        print(f"  Chat ID: {citation['chat_id']}")
        print(f"  Preview: {citation['text_preview']}")
    
    # Test hit rate calculation
    expected_sources = ["state_parquet"]
    hit_rate = evaluator.calculate_retrieval_hit_rate(sample_response, expected_sources)
    
    print(f"\nHit Rate Calculation:")
    print(f"Expected Sources: {expected_sources}")
    print(f"Actual Sources: {[c['source'] for c in citations]}")
    print(f"Hit Rate: {hit_rate:.2f}")

if __name__ == "__main__":
    test_citation_extraction()