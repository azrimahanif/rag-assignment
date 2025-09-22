#!/usr/bin/env python3
"""
Data query and CSV export script for DOSM Population data
"""
import requests
import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Any
import json

def fetch_malaysia_population() -> pd.DataFrame:
    """Fetch Malaysia population data from API"""
    url = "https://api.data.gov.my/data-catalogue"
    params = {
        "id": "population_malaysia",
        "limit": 1000
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df['state'] = 'Malaysia'
        df['data_source'] = 'malaysia_api'
        
        print(f"Malaysia data: {len(df)} records")
        return df
        
    except Exception as e:
        print(f"Error fetching Malaysia data: {e}")
        return pd.DataFrame()

def fetch_state_population() -> pd.DataFrame:
    """Fetch state population data from parquet"""
    try:
        url = 'https://storage.dosm.gov.my/population/population_state.parquet'
        df = pd.read_parquet(url)
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # Filter for target states
        target_states = ['Kedah', 'Selangor']
        filtered_df = df[df['state'].isin(target_states)]
        filtered_df['data_source'] = 'state_parquet'
        
        print(f"State data: {len(filtered_df)} records")
        return filtered_df
        
    except Exception as e:
        print(f"Error fetching state data: {e}")
        return pd.DataFrame()

def analyze_data(df: pd.DataFrame):
    """Analyze and print data summary"""
    print("\n" + "="*50)
    print("DATA ANALYSIS")
    print("="*50)
    
    print(f"Total records: {len(df)}")
    print(f"States covered: {df['state'].unique().tolist()}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Sex categories: {df['sex'].unique().tolist()}")
    print(f"Age groups: {sorted(df['age'].unique().tolist())}")
    print(f"Ethnicity categories: {df['ethnicity'].unique().tolist()}")
    
    print("\nPopulation by State:")
    pop_by_state = df[df['age'] == 'overall'].groupby('state')['population'].sum()
    for state, pop in pop_by_state.items():
        print(f"  {state}: {pop:,.0f} thousand people")
    
    print("\nSample records:")
    print(df.head(10).to_string(index=False))

def export_to_csv(df: pd.DataFrame, filename: str = None):
    """Export data to CSV"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"population_data_{timestamp}.csv"
    
    try:
        df.to_csv(filename, index=False)
        print(f"\nData exported to: {filename}")
        print(f"File size: {os.path.getsize(filename) / 1024:.2f} KB")
        return filename
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return None

def create_sample_queries(df: pd.DataFrame):
    """Create sample queries for testing the RAG system"""
    print("\n" + "="*50)
    print("SAMPLE QUERIES FOR RAG TESTING")
    print("="*50)
    
    queries = [
        "What is the total population of Malaysia?",
        "How many people live in Selangor?",
        "What is the population of Kedah?",
        "Show me the population breakdown by gender in Malaysia",
        "What is the population distribution by age group in Selangor?",
        "Compare the population of Kedah and Selangor",
        "What is the Malay population in Malaysia?",
        "How many elderly people (65+) are there in Selangor?",
        "What is the Chinese population in Kedah?",
        "Show population trends over the years"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"{i:2d}. {query}")

def main():
    """Main execution function"""
    print("DOSM Population Data Query and Export")
    print("=" * 50)
    
    # Fetch data
    print("Fetching Malaysia population data...")
    malaysia_df = fetch_malaysia_population()
    
    print("Fetching state population data...")
    state_df = fetch_state_population()
    
    # Combine data
    print("\nCombining datasets...")
    combined_df = pd.concat([malaysia_df, state_df], ignore_index=True)
    
    if combined_df.empty:
        print("No data fetched!")
        return
    
    # Analyze data
    analyze_data(combined_df)
    
    # Export to CSV
    csv_file = export_to_csv(combined_df)
    
    # Create sample queries
    create_sample_queries(combined_df)
    
    # Save sample queries to file
    sample_queries = [
        "What is the total population of Malaysia?",
        "How many people live in Selangor?",
        "What is the population of Kedah?",
        "Show me the population breakdown by gender in Malaysia",
        "What is the population distribution by age group in Selangor?",
        "Compare the population of Kedah and Selangor",
        "What is the Malay population in Malaysia?",
        "How many elderly people (65+) are there in Selangor?",
        "What is the Chinese population in Kedah?",
        "Show population trends over the years"
    ]
    
    with open('sample_queries.txt', 'w') as f:
        f.write("Sample Queries for Population RAG System\n")
        f.write("="*50 + "\n\n")
        for i, query in enumerate(sample_queries, 1):
            f.write(f"{i:2d}. {query}\n")
    
    print(f"\nSample queries saved to: sample_queries.txt")
    print("\nReview complete! Ready to proceed with data ingestion.")

if __name__ == "__main__":
    main()