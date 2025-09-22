#!/usr/bin/env python3
"""
Direct webhook test script to see raw RAG system output
"""

import requests
import time
import json

def test_webhook_directly():
    """Test the webhook directly and show raw output"""
    webhook_url = "http://localhost:5678/webhook/845822db-ce1a-45df-998c-2dc16278785e/chat"
    
    # Test query
    test_params = {
        "sessionId": "test_direct_session",
        "chatInput": "What was Malaysia's total population in 2023?",
        "conversation_id": "1",
        "message_id": "1"
    }
    
    print("Testing Webhook Directly")
    print("=" * 50)
    print(f"URL: {webhook_url}")
    print(f"Query: {test_params['chatInput']}")
    print("-" * 50)
    
    try:
        start_time = time.time()
        response = requests.get(webhook_url, params=test_params, timeout=60)
        response_time = time.time() - start_time
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Time: {response_time:.2f}s")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        print()
        
        print("Raw Response Content:")
        print("-" * 30)
        try:
            json_response = response.json()
            print(json.dumps(json_response, indent=2))
        except:
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (60s)")
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_multiple_queries():
    """Test a few different queries to see patterns"""
    webhook_url = "http://localhost:5678/webhook/845822db-ce1a-45df-998c-2dc16278785e/chat"
    
    test_queries = [
        "What was Malaysia's total population in 2023?",
        "How many people lived in Selangor in 2024?", 
        "Compare Kedah and Selangor population"
    ]
    
    print("\nTesting Multiple Queries")
    print("=" * 50)
    
    for i, query in enumerate(test_queries):
        print(f"\nQuery {i+1}: {query}")
        print("-" * 40)
        
        params = {
            "sessionId": f"test_session_{i}",
            "chatInput": query,
            "conversation_id": str(i+1),
            "message_id": str(i+1)
        }
        
        try:
            start_time = time.time()
            response = requests.get(webhook_url, params=params, timeout=60)
            response_time = time.time() - start_time
            
            print(f"Status: {response.status_code}, Time: {response_time:.2f}s")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    content = data.get('content', '').strip()
                    print(f"Content: {content[:200]}{'...' if len(content) > 200 else ''}")
                    
                    if 'documents' in data:
                        print(f"Documents: {len(data['documents'])}")
                        for j, doc in enumerate(data['documents'][:2]):  # Show first 2
                            print(f"  Doc {j+1}: {doc.get('data_source', 'unknown')} - {str(doc.get('text', ''))[:100]}...")
                except:
                    print("Invalid JSON response")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Failed: {e}")

if __name__ == "__main__":
    test_webhook_directly()
    test_multiple_queries()