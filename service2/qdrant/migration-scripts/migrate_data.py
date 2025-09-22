#!/usr/bin/env python3
"""
Data migration script to populate Qdrant with population data
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from app.services.qdrant_service import QdrantService
from app.services.openai_service import OpenAIService
from app.core.config import settings
from app.core.logging import setup_logging, get_logger

import pandas as pd
import requests
import json
from typing import List, Dict, Any

# Setup logging
setup_logging()
logger = get_logger(__name__)


class PopulationDataMigrator:
    """Handle migration of population data to Qdrant"""
    
    def __init__(self):
        self.qdrant_service = QdrantService()
        self.openai_service = OpenAIService()
        
    async def fetch_population_data(self) -> List[Dict]:
        """Fetch population data from DOSM sources"""
        
        all_data = []
        
        try:
            # Fetch Malaysia overall population data
            logger.info("Fetching Malaysia population data...")
            malaysia_url = "https://api.data.gov.my/data-catalogue"
            malaysia_params = {
                "id": "population_malaysia",
                "limit": 1000
            }
            
            malaysia_response = requests.get(malaysia_url, params=malaysia_params)
            malaysia_response.raise_for_status()
            malaysia_data = malaysia_response.json()
            
            # Add state identifier to Malaysia data
            for item in malaysia_data:
                item['state'] = 'Malaysia'
                item['data_source'] = 'malaysia_api'
            
            all_data.extend(malaysia_data)
            logger.info(f"Malaysia records: {len(malaysia_data)}")
            
            # Fetch state population data (Kedah and Selangor)
            logger.info("Fetching state population data...")
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
            logger.info(f"State records (Kedah, Selangor): {len(state_data)}")
            
            logger.info(f"Total population records: {len(all_data)}")
            return all_data
            
        except Exception as e:
            logger.error("Error fetching population data", error=str(e))
            return []
    
    def process_population_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Process raw population data using Year-State-Demographic chunking strategy"""
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(raw_data)
        
        # Convert date to datetime and extract year
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        
        processed_chunks = []
        
        # Group by year and state (optimized chunking strategy)
        for (year, state), group in df.groupby(['year', 'state']):
            chunk = self.create_year_state_chunk(group, year, state)
            if chunk:
                processed_chunks.append(chunk)
        
        logger.info(f"Created {len(processed_chunks)} chunks using Year-State-Demographic strategy")
        return processed_chunks
    
    def create_year_state_chunk(self, group: pd.DataFrame, year: int, state: str) -> Dict:
        """Create a single chunk for a year-state combination with demographic breakdown"""
        
        # Get overall population for this year-state
        overall_data = group[group['age'] == 'overall']
        total_population = overall_data[overall_data['sex'] == 'both']['population'].iloc[0] if not overall_data.empty else 0
        
        # Create demographic breakdowns
        demographics = self.create_demographic_breakdown(group)
        
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
            "age_groups": list(demographics.get('age_breakdown', {}).keys()),
            "sex_categories": list(demographics.get('gender_breakdown', {}).keys()),
            "ethnicity_categories": list(demographics.get('ethnicity_breakdown', {}).keys()),
            "ingestion_timestamp": datetime.now().isoformat()
        }
        
        return {
            "text": chunk_text.strip(),
            "metadata": metadata
        }
    
    def create_demographic_breakdown(self, group: pd.DataFrame) -> Dict:
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
    
    def convert_numpy_types(self, obj):
        """Convert numpy types to native Python types for JSON serialization"""
        import numpy as np
        
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self.convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_numpy_types(item) for item in obj]
        elif isinstance(obj, type(dict().keys())):
            return list(obj)
        else:
            return obj
    
    async def migrate_to_qdrant(self, chunks: List[Dict]) -> bool:
        """Migrate processed chunks to Qdrant"""
        
        if not chunks:
            logger.warning("No chunks to migrate")
            return False
        
        logger.info(f"Starting migration of {len(chunks)} chunks to Qdrant")
        
        # Ensure collection exists
        await self.qdrant_service.ensure_collection_exists()
        
        # Process in batches to avoid memory issues
        batch_size = 50
        total_processed = 0
        
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            
            # Generate embeddings for batch
            texts = [chunk["text"] for chunk in batch_chunks]
            try:
                embeddings = await self.openai_service.create_batch_embeddings(texts)
                
                if not embeddings:
                    logger.error("Failed to generate embeddings for batch")
                    continue
                
                # Create Qdrant points
                points = []
                for j, (chunk, embedding) in enumerate(zip(batch_chunks, embeddings)):
                    # Convert numpy types to native Python types
                    clean_metadata = self.convert_numpy_types(chunk["metadata"])
                    
                    from qdrant_client.models import PointStruct
                    point = PointStruct(
                        id=i + j,
                        vector=embedding,
                        payload={
                            "text": chunk["text"],
                            "metadata": clean_metadata
                        }
                    )
                    points.append(point)
                
                # Upsert batch to Qdrant
                await self.qdrant_service.upsert_points(points)
                
                total_processed += len(points)
                logger.info(f"Processed batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}, "
                           f"total points: {total_processed}/{len(chunks)}")
                
            except Exception as e:
                logger.error(f"Failed to process batch {i//batch_size + 1}", error=str(e))
                continue
        
        logger.info(f"Migration completed successfully. Total points: {total_processed}")
        return True
    
    async def run_migration(self):
        """Run the complete migration process"""
        
        logger.info("Starting population data migration")
        
        # Step 1: Fetch raw data
        logger.info("Step 1: Fetching raw population data...")
        raw_data = await self.fetch_population_data()
        
        if not raw_data:
            logger.error("No data fetched, migration aborted")
            return False
        
        # Step 2: Process data into chunks
        logger.info("Step 2: Processing data into chunks...")
        processed_chunks = self.process_population_data(raw_data)
        
        if not processed_chunks:
            logger.error("No chunks created, migration aborted")
            return False
        
        # Step 3: Migrate to Qdrant
        logger.info("Step 3: Migrating to Qdrant...")
        success = await self.migrate_to_qdrant(processed_chunks)
        
        if success:
            logger.info("Migration completed successfully!")
            
            # Get final collection stats
            try:
                collection_stats = await self.qdrant_service.get_collection_stats()
                logger.info("Final collection statistics:", stats=collection_stats)
            except Exception as e:
                logger.error("Failed to get final collection stats", error=str(e))
            
            return True
        else:
            logger.error("Migration failed")
            return False


async def main():
    """Main migration function"""
    
    migrator = PopulationDataMigrator()
    
    try:
        success = await migrator.run_migration()
        if success:
            print("✅ Migration completed successfully!")
            return 0
        else:
            print("❌ Migration failed!")
            return 1
            
    except Exception as e:
        logger.error("Migration failed with exception", error=str(e))
        print(f"❌ Migration failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)