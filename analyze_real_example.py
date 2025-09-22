#!/usr/bin/env python3
"""
Analyze the real AI agent example with URL-encoded JSON
"""

import urllib.parse
import json

def analyze_real_example():
    """Analyze the real AI agent example"""

    # The actual AI response from the user
    ai_response = """In 2023, Selangor's total population reached 7,209,700, while Kedah's was 2,189,300. Selangor was not only much more populous but also more ethnically diverse. The Bumi Malay population stood at 3,956,800 in Selangor (about 54.9% of the total) compared to 1,682,000 in Kedah (76.8%). The Chinese community in Selangor numbered 1,758,700, far higher than Kedah's 248,600. The Indian population in Selangor was 729,100, again much higher than Kedah's 128,600.

Noncitizens made up a more significant share in Selangor (624,900) than in Kedah (99,600). Similarly, the population of other citizens was slightly higher in Selangor at 56,400 compared to Kedah's 25,800.

This data covers state-level populations for 2023, broken down by ethnicity and citizenship status, reflecting continuously higher diversity and urbanisation in Selangor versus Kedah's more homogenous composition.

If you'd like further breakdowns by age, gender, or district, let me know—or you can visit the DOSM portal for the latest detailed figures.

Source: state_parquet, DOSM 2023

Chart: https://quickchart.io/chart?width=200&c=%7B%22type%22%3A%22bar%22%2C%22data%22%3A%7B%22labels%22%3A%5B%22Selangor%22%2C%22Kedah%22%5D%2C%22datasets%22%3A%5B%7B%22label%22%3A%22Total%20Population%22%2C%22data%22%3A%5B7209.7%2C2189.3%5D%2C%22backgroundColor%22%3A%5B%22rgba(75%2C%20192%2C%20192%2C%200.2)%22%5D%2C%22borderColor%22%3A%5B%22rgba(75%2C%20192%2C%20192%2C%201)%22%5D%2C%22borderWidth%22%3A1%7D%2C%7B%22label%22%3A%22Bumi%20Malay%22%2C%22data%22%3A%5B3956.8%2C1682.0%5D%2C%22backgroundColor%22%3A%5B%22rgba(255%2C%2099%2C%20132%2C%200.2)%22%5D%2C%22borderColor%22%3A%5B%22rgba(255%2C%2099%2C%20132%2C%201)%22%5D%2C%22borderWidth%22%3A1%7D%2C%7B%22label%22%3A%22Chinese%22%2C%22data%22%3A%5B1758.7%2C248.6%5D%2C%22backgroundColor%22%3A%5B%22rgba(54%2C%20162%2C%20235%2C%200.2)%22%5D%2C%22borderColor%22%3A%5B%22rgba(54%2C%20162%2C%20235%2C%201)%22%5D%2C%22borderWidth%22%3A1%7D%2C%7B%22label%22%3A%22Indian%22%2C%22data%22%3A%5B729.1%2C128.6%5D%2C%22backgroundColor%22%3A%5B%22rgba(255%2C%20206%2C%2086%2C%200.2)%22%5D%2C%22borderColor%22%3A%5B%22rgba(255%2C%20206%2C%2086%2C%201)%22%5D%2C%22borderWidth%22%3A1%7D%2C%7B%22label%22%3A%22Other%20Citizen%22%2C%22data%22%3A%5B56.4%2C25.8%5D%2C%22backgroundColor%22%3A%5B%22rgba(153%2C%20102%2C%20255%2C%200.2)%22%5D%2C%22borderColor%22%3A%5B%22rgba(153%2C%20102%2C%20255%2C%201)%22%5D%2C%22borderWidth%22%3A1%7D%2C%7B%22label%22%3A%22Noncitizen%22%2C%22data%22%3A%5B624.9%2C99.6%5D%2C%22backgroundColor%22%3A%5B%22rgba(255%2C%20159%2C%2064%2C%200.2)%22%5D%2C%22borderColor%22%3A%5B%22rgba(255%2C%20159%2C%2064%2C%201)%22%5D%2C%22borderWidth%22%3A1%7D%5D%7D%2C%22options%22%3A%7B%22scales%22%3A%7B%22yAxes%22%3A%5B%7B%22ticks%22%3A%7B%22max%22%3A7500%2C%22min%22%3A0%2C%22stepSize%22%3A500%2C%22beginAtZero%22%3Atrue%7D%2C%22stacked%22%3Afalse%7D%5D%2C%22xAxes%22%3A%7B%22stacked%22%3Atrue%7D%7D%2C%22plugins%22%3A%7B%22title%22%3A%7B%22display%22%3Atrue%2C%22text%22%3A%22Population%20Comparison%20between%20Selangor%20and%20Kedah%20in%202023%22%7D%2C%22legend%22%3A%7B%22display%22%3Atrue%2C%22position%22%3A%22top%22%7D%7D%7D%7D"""

    print("Analyzing Real AI Agent Example")
    print("=" * 50)

    # Extract the URL
    import re
    bare_url_pattern = r'https?:\/\/quickchart\.io\/chart\?[^\s)]+'
    match = re.search(bare_url_pattern, ai_response)

    if match:
        bare_url = match[0]
        print(f"Found URL: {bare_url[:100]}...")

        # Parse the URL
        parsed_url = urllib.parse.urlparse(bare_url)
        params = urllib.parse.parse_qs(parsed_url.query)

        print(f"\nURL Parameters:")
        for key, value in params.items():
            print(f"  {key}: {value[0][:50]}...")

        # Get the config parameter
        config_param = params.get('c', [None])[0]
        if config_param:
            print(f"\nConfig parameter (URL-encoded):")
            print(f"  {config_param[:100]}...")

            # Decode the URL-encoded JSON
            try:
                decoded_config = urllib.parse.unquote(config_param)
                print(f"\nDecoded config:")
                print(f"  {decoded_config[:200]}...")

                # Parse as JSON
                config_json = json.loads(decoded_config)
                print(f"\nParsed JSON structure:")
                print(f"  Type: {config_json.get('type')}")
                print(f"  Labels: {config_json.get('data', {}).get('labels')}")
                print(f"  Datasets: {len(config_json.get('data', {}).get('datasets', []))} datasets")
                print(f"  Title: {config_json.get('options', {}).get('plugins', {}).get('title', {}).get('text')}")

                print(f"\nDataset labels:")
                for dataset in config_json.get('data', {}).get('datasets', []):
                    print(f"  - {dataset.get('label')}: {dataset.get('data')}")

                print(f"\nCurrent issue analysis:")
                print(f"  ✅ URL detection: Works")
                print(f"  ✅ URL normalization: Works (adds format=png)")
                print(f"  ❌ JSON processing: URL-encoded JSON not decoded")
                print(f"  ❌ Title extraction: Cannot extract from encoded JSON")
                print(f"  ❌ Chart rendering: QuickChart receives encoded JSON, fails to parse")

            except Exception as e:
                print(f"Error processing config: {e}")

    print("\n" + "=" * 50)
    print("Problem Summary:")
    print("1. AI agents provide URL-encoded JSON in QuickChart URLs")
    print("2. Current normalizeQuickChartUrl() preserves the encoded JSON")
    print("3. QuickChart service cannot parse URL-encoded JSON")
    print("4. Need to decode JSON before sending to QuickChart")
    print("5. Also need to extract title from the decoded JSON")

if __name__ == "__main__":
    analyze_real_example()