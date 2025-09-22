#!/usr/bin/env python3
"""
Simple API call to fetch DOSM population data for review
"""
import requests
import pandas as pd
import json
from datetime import datetime, timedelta

def fetch_malaysia_population():
    """Fetch Malaysia population data"""
    url = "https://api.data.gov.my/data-catalogue"
    params = {
        "id": "population_malaysia",
        "limit": 1000
    }
    
    print("Fetching Malaysia population data...")
    response = requests.get(url, params=params)
    data = response.json()
    
    print(f"Malaysia data: {len(data)} records")
    return data

def fetch_state_population():
    """Fetch state population data (Kedah & Selangor)"""
    url = 'https://storage.dosm.gov.my/population/population_state.parquet'
    
    print("Fetching state population data...")
    df = pd.read_parquet(url)
    
    # Filter for target states
    target_states = ['Kedah', 'Selangor']
    filtered_df = df[df['state'].isin(target_states)]
    
    print(f"State data: {len(filtered_df)} records")
    return filtered_df.to_dict('records')

def main():
    """Simple data fetch and CSV export"""
    print("DOSM Population Data - Raw Data to CSV")
    print("=" * 50)
    
    # Malaysia data
    malaysia_data = fetch_malaysia_population()
    malaysia_df = pd.DataFrame(malaysia_data)
    malaysia_df['state'] = 'Malaysia'
    malaysia_df['data_source'] = 'malaysia_api'
    
    # State data
    state_data = fetch_state_population()
    state_df = pd.DataFrame(state_data)
    state_df['data_source'] = 'state_parquet'
    
    # Convert date columns to string format
    if 'date' in malaysia_df.columns:
        malaysia_df['date'] = malaysia_df['date'].astype(str)
    if 'date' in state_df.columns:
        state_df['date'] = state_df['date'].astype(str)
    
    # Combine data
    combined_df = pd.concat([malaysia_df, state_df], ignore_index=True)
    
    # Sort by state and date
    combined_df = combined_df.sort_values(['state', 'date'])
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"population_data_{timestamp}.csv"
    
    combined_df.to_csv(csv_filename, index=False)
    
    # Display sample data
    print("\nSample Data (first 10 rows):")
    print(combined_df.head(10).to_string(index=False))
    
    print(f"\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Total Malaysia records: {len(malaysia_df)}")
    print(f"Total state records: {len(state_df)}")
    print(f"Combined total: {len(combined_df)}")
    print(f"States covered: {combined_df['state'].unique().tolist()}")
    print(f"Date range: {combined_df['date'].min()} to {combined_df['date'].max()}")
    print(f"Columns: {list(combined_df.columns)}")
    
    print(f"\nData saved to: {csv_filename}")
    print(f"File size: {len(combined_df)} rows")

if __name__ == "__main__":
    main()