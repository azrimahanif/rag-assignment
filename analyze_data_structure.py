#!/usr/bin/env python3
"""
Analyze population data structure for vector DB design
"""
import pandas as pd

# Load the CSV file
df = pd.read_csv('population_data_20250911_111447.csv')

print("POPULATION DATA ANALYSIS")
print("=" * 60)

# Basic info
print(f"Total records: {len(df)}")
print(f"Columns: {list(df.columns)}")

# Unique values for each column
print("\nUNIQUE VALUES BY COLUMN:")
print("-" * 30)

print(f"States: {sorted(df['state'].unique())}")
print(f"Sex categories: {sorted(df['sex'].unique())}")
print(f"Age groups: {sorted(df['age'].unique())}")
print(f"Ethnicity categories: {sorted(df['ethnicity'].unique())}")
print(f"Data sources: {sorted(df['data_source'].unique())}")

# Date range
df['date'] = pd.to_datetime(df['date'])
print(f"\nDate range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
print(f"Years covered: {sorted(df['date'].dt.year.unique())}")

# Data distribution
print("\nDATA DISTRIBUTION:")
print("-" * 30)

print("Records by state:")
print(df['state'].value_counts())

print("\nRecords by data source:")
print(df['data_source'].value_counts())

# Sample recent data
print("\nRECENT DATA SAMPLE (2023-2025):")
print("-" * 30)
recent_data = df[df['date'].dt.year >= 2023].head(10)
print(recent_data[['state', 'date', 'age', 'sex', 'ethnicity', 'population']].to_string(index=False))

# Chunking strategy analysis
print("\nCHUNKING STRATEGY ANALYSIS:")
print("-" * 30)

# Group by date to see how much data per year
yearly_counts = df.groupby(df['date'].dt.year).size()
print("Records per year:")
print(yearly_counts.tail(10))  # Last 10 years

# Group by state and date to see combinations
state_date_combinations = df.groupby(['state', df['date'].dt.year]).size()
print(f"\nState-year combinations: {len(state_date_combinations)}")

# Suggested chunking approach
print("\nSUGGESTED CHUNKING APPROACH:")
print("-" * 30)
print("1. BY YEAR & STATE (Recommended)")
print("   - Group by year + state + demographics")
print("   - Good for temporal queries")
print("   - Manageable chunk sizes")

print("\n2. BY DEMOGRAPHIC BREAKDOWN")
print("   - Group by age + sex + ethnicity combinations")
print("   - Good for demographic analysis")

print("\n3. HYBRID APPROACH")
print("   - Year-state as primary grouping")
print("   - Include demographic context in text")