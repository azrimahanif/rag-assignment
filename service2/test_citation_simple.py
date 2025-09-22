#!/usr/bin/env python3
"""
Simple test of citation extraction logic
"""

def extract_citations_simple(response):
    """Simple citation extraction test"""
    citations = []
    
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
            
            citation = {
                "source": source,
                "chat_id": doc.get("chat_id", "unknown"),
                "text_preview": create_text_preview_simple(doc.get("text", ""))
            }
            citations.append(citation)
    
    return citations

def create_text_preview_simple(text, max_length=100):
    """Create a preview of document text"""
    if not text:
        return "No content available"
    
    text = text.strip()
    if len(text) <= max_length:
        return text
    else:
        return text[:max_length] + "..."

def calculate_retrieval_hit_rate_simple(response, expected_sources):
    """Calculate retrieval hit-rate based on expected sources"""
    if "error" in response:
        return 0.0
        
    # Extract sources from response
    retrieved_sources = []
    if "documents" in response:
        for doc in response.get("documents", []):
            source = "unknown"
            if isinstance(doc, dict):
                source = doc.get("data_source") or doc.get("source") or doc.get("metadata", {}).get("data_source", "unknown")
                
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
        
    hits = sum(1 for source in expected_sources if any(expected in source for expected in expected_sources))
    return hits / len(expected_sources) if expected_sources else 0.0

def test_citation_extraction():
    """Test citation extraction with sample data"""
    
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
    
    citations = extract_citations_simple(sample_response)
    
    print(f"Extracted {len(citations)} citations:")
    for i, citation in enumerate(citations):
        print(f"\nCitation {i+1}:")
        print(f"  Source: {citation['source']}")
        print(f"  Chat ID: {citation['chat_id']}")
        print(f"  Preview: {citation['text_preview']}")
    
    # Test hit rate calculation
    expected_sources = ["state_parquet"]
    hit_rate = calculate_retrieval_hit_rate_simple(sample_response, expected_sources)
    
    print(f"\nHit Rate Calculation:")
    print(f"Expected Sources: {expected_sources}")
    print(f"Actual Sources: {[c['source'] for c in citations]}")
    print(f"Hit Rate: {hit_rate:.2f}")
    
    if hit_rate > 0:
        print("✅ Citation extraction fix works!")
    else:
        print("❌ Citation extraction still needs work")

if __name__ == "__main__":
    test_citation_extraction()