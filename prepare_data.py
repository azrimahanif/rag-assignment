#!/usr/bin/env python3
"""
Data preparation script for DOSM CPI data to Qdrant vector database
"""
import requests
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from qdrant_client.http.models import CollectionInfo
import openai
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "dosm_population_data")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"

# Data Configuration
TARGET_STATES = ["Malaysia", "Kedah", "Selangor"]

# Initialize clients - using local Qdrant (no API key needed) with timeout
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    timeout=30  # Increase timeout to 30 seconds
)

def fetch_population_data() -> List[Dict]:
    """Fetch Population data from DOSM API"""
    import pandas as pd
    
    all_data = []
    
    try:
        # Fetch Malaysia overall population data
        malaysia_url = "https://api.data.gov.my/data-catalogue"
        malaysia_params = {
            "id": "population_malaysia",
            "limit": 1000
        }
        
        print("Fetching Malaysia population data...")
        malaysia_response = requests.get(malaysia_url, params=malaysia_params)
        malaysia_response.raise_for_status()
        malaysia_data = malaysia_response.json()
        
        # Add state identifier to Malaysia data
        for item in malaysia_data:
            item['state'] = 'Malaysia'
            item['data_source'] = 'malaysia_api'
        
        all_data.extend(malaysia_data)
        print(f"Malaysia records: {len(malaysia_data)}")
        
        # Fetch state population data (Kedah and Selangor)
        print("Fetching state population data...")
        state_url = 'https://storage.dosm.gov.my/population/population_state.parquet'
        
        # Read parquet file
        df = pd.read_parquet(state_url)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # Filter for target states and convert to dict
        target_states = ['Kedah', 'Selangor']
        filtered_df = df[df['state'].isin(target_states)]
        
        # Convert to list of dictionaries
        state_data = filtered_df.to_dict('records')
        
        # Add data source identifier
        for item in state_data:
            item['data_source'] = 'state_parquet'
            item['date'] = item['date'].strftime('%Y-%m-%d') if pd.notnull(item['date']) else None
        
        all_data.extend(state_data)
        print(f"State records (Kedah, Selangor): {len(state_data)}")
        
        print(f"Total population records: {len(all_data)}")
        return all_data
        
    except Exception as e:
        print(f"Error fetching population data: {e}")
        return []

def process_population_data(raw_data: List[Dict]) -> List[Dict]:
    """Process raw Population data using Year-State-Demographic chunking strategy"""
    # Convert to DataFrame for easier processing
    df = pd.DataFrame(raw_data)
    
    # Convert date to datetime and extract year
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    
    processed_chunks = []
    
    # Group by year and state (optimized chunking strategy)
    for (year, state), group in df.groupby(['year', 'state']):
        chunk = create_year_state_chunk(group, year, state)
        if chunk:
            processed_chunks.append(chunk)
    
    print(f"Created {len(processed_chunks)} chunks using Year-State-Demographic strategy")
    return processed_chunks

def create_year_state_chunk(group: pd.DataFrame, year: int, state: str) -> Dict:
    """Create a single chunk for a year-state combination with demographic breakdown"""
    
    # Get overall population for this year-state
    overall_data = group[group['age'] == 'overall']
    total_population = overall_data[overall_data['sex'] == 'both']['population'].iloc[0] if not overall_data.empty else 0
    
    # Create demographic breakdowns
    demographics = create_demographic_breakdown(group)
    
    # Create descriptive text for embedding
    chunk_text = f"""Population data for {state} in {year}.
    
Total population: {total_population:,.1f} thousand people.

Gender Breakdown:
"""
    
    # Add gender information
    if 'gender_breakdown' in demographics:
        for gender, pop in demographics['gender_breakdown'].items():
            chunk_text += f"- {gender.title()}: {pop:,.1f}k ({pop/total_population*100:.1f}%)\n"
    
    chunk_text += "\nAge Distribution:\n"
    if 'age_breakdown' in demographics:
        for age_group, pop in demographics['age_breakdown'].items():
            chunk_text += f"- {age_group}: {pop:,.1f}k ({pop/total_population*100:.1f}%)\n"
    
    chunk_text += "\nEthnic Composition:\n"
    if 'ethnicity_breakdown' in demographics:
        for ethnicity, pop in demographics['ethnicity_breakdown'].items():
            chunk_text += f"- {ethnicity.replace('_', ' ').title()}: {pop:,.1f}k ({pop/total_population*100:.1f}%)\n"
    
    chunk_text += f"\nData source: {group['data_source'].iloc[0] if not group.empty else 'Unknown'}"
    chunk_text += f"\nCoverage: {len(group)} demographic data points"
    
    # Create metadata
    metadata = {
        "chunk_id": f"{state}_{year}",
        "state": state,
        "year": year,
        "date_range": f"{year}-01-01",
        "total_population": float(total_population) if total_population else 0,
        "data_points": len(group),
        "data_source": group['data_source'].iloc[0] if not group.empty else 'Unknown',
        "demographics": demographics,
        "age_groups": demographics.get('age_breakdown', {}).keys(),
        "sex_categories": demographics.get('gender_breakdown', {}).keys(),
        "ethnicity_categories": demographics.get('ethnicity_breakdown', {}).keys(),
        "ingestion_timestamp": datetime.now().isoformat()
    }
    
    return {
        "text": chunk_text.strip(),
        "metadata": metadata
    }

def create_demographic_breakdown(group: pd.DataFrame) -> Dict:
    """Create demographic breakdowns from grouped data"""
    demographics = {}
    
    # Gender breakdown (from overall age group)
    overall_age = group[group['age'] == 'overall']
    if not overall_age.empty:
        gender_data = overall_age[overall_age['ethnicity'] == 'overall']
        if not gender_data.empty:
            demographics['gender_breakdown'] = {
                row['sex']: row['population'] 
                for _, row in gender_data.iterrows()
            }
    
    # Age breakdown (from both sexes, overall ethnicity)
    both_sexes = group[(group['sex'] == 'both') & (group['ethnicity'] == 'overall')]
    if not both_sexes.empty:
        demographics['age_breakdown'] = {
            row['age']: row['population'] 
            for _, row in both_sexes.iterrows()
            if row['age'] != 'overall'  # Skip overall to avoid double-counting
        }
    
    # Ethnicity breakdown (from both sexes, overall age)
    overall_both = group[(group['sex'] == 'both') & (group['age'] == 'overall')]
    if not overall_both.empty:
        demographics['ethnicity_breakdown'] = {
            row['ethnicity']: row['population'] 
            for _, row in overall_both.iterrows()
            if row['ethnicity'] != 'overall'  # Skip overall to avoid double-counting
        }
    
    return demographics

def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    import numpy as np
    
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, type(dict().keys())):
        return list(obj)
    else:
        return obj

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using OpenAI API"""
    try:
        response = openai.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL,
            input=texts
        )
        return [embedding.embedding for embedding in response.data]
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return []

def setup_qdrant_collection():
    """Create Qdrant collection if it doesn't exist"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            collections = qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if QDRANT_COLLECTION not in collection_names:
                qdrant_client.create_collection(
                    collection_name=QDRANT_COLLECTION,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
                )
                print(f"Collection '{QDRANT_COLLECTION}' created successfully")
            else:
                print(f"Collection '{QDRANT_COLLECTION}' already exists")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                import time
                time.sleep(2)  # Wait 2 seconds before retry
            else:
                print(f"Error setting up collection after {max_retries} attempts: {e}")

def store_in_qdrant(chunks: List[Dict]):
    """Store processed chunks in Qdrant"""
    texts = [chunk["text"] for chunk in chunks]
    embeddings = generate_embeddings(texts)
    
    if not embeddings:
        print("No embeddings generated, skipping storage")
        return
    
    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        # Convert numpy types to native Python types
        clean_metadata = convert_numpy_types(chunk["metadata"])
        
        point = PointStruct(
            id=i,
            vector=embedding,
            payload={
                "text": chunk["text"],
                "metadata": clean_metadata
            }
        )
        points.append(point)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            qdrant_client.upsert(
                collection_name=QDRANT_COLLECTION,
                points=points
            )
            print(f"Successfully stored {len(points)} points in Qdrant")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Upload attempt {attempt + 1} failed: {e}. Retrying...")
                import time
                time.sleep(3)  # Wait 3 seconds before retry
            else:
                print(f"Error storing in Qdrant after {max_retries} attempts: {e}")

def main():
    """Main execution function"""
    print("Starting population data preparation for Qdrant...")
    print("Using optimized Year-State-Demographic chunking strategy")
    
    # Fetch data from DOSM API
    print("Fetching population data from DOSM API...")
    raw_data = fetch_population_data()
    print(f"Fetched {len(raw_data)} records")
    
    # Process data with new chunking strategy
    print("Processing population data with optimized chunking...")
    processed_chunks = process_population_data(raw_data)
    print(f"Created {len(processed_chunks)} chunks")
    
    # Show sample chunk
    if processed_chunks:
        print("\nSample chunk structure:")
        sample_chunk = processed_chunks[0]
        print(f"Chunk ID: {sample_chunk['metadata']['chunk_id']}")
        print(f"State: {sample_chunk['metadata']['state']}")
        print(f"Year: {sample_chunk['metadata']['year']}")
        print(f"Total Population: {sample_chunk['metadata']['total_population']}")
        print(f"Data Points: {sample_chunk['metadata']['data_points']}")
        print(f"Text length: {len(sample_chunk['text'])} characters")
        print(f"Metadata keys: {list(sample_chunk['metadata'].keys())}")
    
    # Setup Qdrant collection
    print("\nSetting up Qdrant collection...")
    setup_qdrant_collection()
    
    # Store in Qdrant
    print("Storing data in Qdrant...")
    store_in_qdrant(processed_chunks)
    
    print("\nPopulation data preparation completed!")
    print(f"Successfully stored {len(processed_chunks)} chunks in Qdrant")

if __name__ == "__main__":
    main()