# Dataset Card: Malaysia Population Data (DOSM)

## Dataset Description

This dataset contains comprehensive population statistics for Malaysia and selected states, compiled from the Department of Statistics Malaysia (DOSM). The data spans 55 years (1970-2025) and includes detailed demographic breakdowns by age, sex, and ethnicity.

### Sources

- **Malaysia Overall Data**: DOSM API - `population_malaysia` endpoint
- **State Data**: DOSM Parquet Files - `population_state.parquet`
- **Data Provider**: Department of Statistics Malaysia (DOSM)
- **Access Method**: Official government API and data portal

### Dataset Summary

- **Total Records**: 35,830 individual data points
- **Time Range**: 1970-2025 (55 years of historical data)
- **Geographic Coverage**: 
  - Malaysia (national level)
  - Kedah (state level)
  - Selangor (state level)
- **Update Frequency**: Annual projections with historical backfill
- **Data Format**: JSON (API) + Parquet (state files)

### Dataset Structure

#### Core Fields

| Field | Type | Description |
|-------|------|-------------|
| `date` | Date | Data collection date (YYYY-MM-DD) |
| `state` | String | Geographic area (Malaysia/Kedah/Selangor) |
| `age` | String | Age group (overall, 0-4, 5-9, ..., 80-84, 85+) |
| `sex` | String | Gender category (both, male, female) |
| `ethnicity` | String | Ethnic group (overall, bumi_malay, chinese, indian, others, non_citizens) |
| `population` | Float | Population count in thousands |
| `data_source` | String | Origin of the data (malaysia_api/state_parquet) |

#### Demographic Breakdown

**Age Groups (21 categories):**
- Overall (all ages combined)
- 0-4, 5-9, 10-14, 15-19, 20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59, 60-64, 65-69, 70-74, 75-79, 80-84, 85+

**Sex Categories (3 categories):**
- Both sexes combined
- Male
- Female

**Ethnicity Categories (9 categories):**
- Overall (all ethnicities combined)
- Bumi Malay
- Chinese
- Indian
- Other Bumiputera
- Others
- Non-citizens

### Data Quality and Limitations

#### Data Quality
- **Completeness**: High completeness for core demographic fields
- **Accuracy**: Official government statistics with standardized methodology
- **Consistency**: Uniform collection methods across time periods
- **Timeliness**: Data updated annually with projections

#### Limitations and Biases
- **Geographic Coverage**: Limited to Malaysia national level and 2 states (Kedah, Selangor)
- **Time Projection**: Data for 2024-2025 includes projected estimates
- **Aggregation Level**: Data is pre-aggregated, limiting granular analysis
- **Ethnic Classification**: Categories reflect Malaysian census classifications
- **Population Units**: All values in thousands (may require conversion for precise calculations)

### Usage Examples

#### Basic Queries
```python
# Get Malaysia's total population in 2023
malaysia_2023 = data[(data['state'] == 'Malaysia') & 
                    (data['date'] == '2023-01-01') & 
                    (data['age'] == 'overall') & 
                    (data['sex'] == 'both') & 
                    (data['ethnicity'] == 'overall')]
```

#### Demographic Analysis
```python
# Age distribution in Selangor 2024
selangor_age = data[(data['state'] == 'Selangor') & 
                   (data['date'] == '2024-01-01') & 
                   (data['sex'] == 'both') & 
                   (data['ethnicity'] == 'overall') & 
                   (data['age'] != 'overall')]
```

### Intended Use Cases

- **Population Research**: Academic and demographic studies
- **Policy Analysis**: Government planning and resource allocation
- **Business Intelligence**: Market analysis and location planning
- **Educational Purposes**: Teaching demographics and data analysis
- **RAG Systems**: Question answering about Malaysian population trends

### Prohibited Uses

- **Individual Identification**: Data cannot be used to identify individuals
- **Discrimination**: Cannot be used for discriminatory purposes
- **Misrepresentation**: Should not be presented as more granular than it is
- **Commercial Exploitation**: Cannot be sold as a standalone product

### Ethical Considerations

- **Data Privacy**: Aggregated data protects individual privacy
- **Cultural Sensitivity**: Ethnic categories reflect official classifications
- **Representation**: Data represents Malaysian population diversity
- **Temporal Context**: Historical data reflects past social contexts

### Maintenance and Updates

- **Source Updates**: DOSM updates data annually
- **Data Freshness**: Projections included for near-term years
- **Version Control**: Dataset versions tracked by collection date
- **Quality Checks**: Regular validation against official sources

### Citation Format

```
Source: DOSM {data_source}, State: {state}, Year: {year}, Data Points: {count}
```

**Example:**
```
Source: DOSM malaysia_api, State: Malaysia, Year: 2024, Data Points: 567
```

### Acknowledgments

This dataset is made possible by the open data initiatives of the Department of Statistics Malaysia (DOSM) and their commitment to transparent and accessible government data.

### Contact and Support

For questions about this dataset card or implementation issues, please refer to the project documentation or create an issue in the project repository.

---

**Dataset Card Version**: 1.0  
**Created**: September 2025  
**Last Updated**: September 2025  
**License**: Government Open Data (follow DOSM terms)