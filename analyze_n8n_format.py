#!/usr/bin/env python3
"""
Test script to analyze the specific n8n output format
"""

import json
import re
import urllib.parse

def analyze_n8n_output():
    """Analyze the specific n8n output format provided by user"""

    n8n_output = '![Population Comparison Kedah vs Selangor 2020](https://quickchart.io/chart?type=bar&data={%22labels%22:[%22Kedah%22,%22Selangor%22],%22datasets%22:[{%22label%22:%22Population%20(thousand)%22,%22data%22:[2131.4,6994.4]}]}&options={%22title%22:{%22display%22:true,%22text%22:%22Population%20Comparison:%20Kedah%20vs%20Selangor%202020%22},%22scales%22:{%22yAxes%22:[{%22ticks%22:{%22beginAtZero%22:true}}]}})'

    print("Analyzing n8n Output Format")
    print("=" * 50)
    print(f"Original n8n output:")
    print(n8n_output)
    print()

    # Test if it matches the markdown pattern from chartRenderer.tsx
    markdown_pattern = r'!\[([^\]]*)\]\((https?:\/\/(?:quickchart\.io\/chart\?[^)]+|(?:%3A%2F%2Fquickchart\.io%2Fchart%3F[^)]+)))\)'

    print("Testing markdown pattern matching...")
    match = re.search(markdown_pattern, n8n_output, re.IGNORECASE)

    if match:
        title = match[1]
        url = match[2]

        print(f"[OK] Pattern MATCHES!")
        print(f"Title: {title}")
        print(f"URL: {url}")
        print()

        # Test URL decoding
        print("Testing URL decoding...")
        try:
            decoded_url = urllib.parse.unquote(url)
            print(f"Decoded URL: {decoded_url}")
            print()

            # Parse the URL parameters
            parsed_url = urllib.parse.urlparse(decoded_url)
            params = urllib.parse.parse_qs(parsed_url.query)

            print("URL Parameters:")
            for key, value in params.items():
                print(f"  {key}: {value}")
            print()

            # Check if data and options are JSON
            if 'data' in params:
                try:
                    data_json = json.loads(params['data'][0])
                    print(f"[OK] Data is valid JSON:")
                    print(f"  {json.dumps(data_json, indent=2)}")
                except json.JSONDecodeError as e:
                    print(f"[FAIL] Data is not valid JSON: {e}")

            if 'options' in params:
                try:
                    options_json = json.loads(params['options'][0])
                    print(f"[OK] Options is valid JSON:")
                    print(f"  {json.dumps(options_json, indent=2)}")
                except json.JSONDecodeError as e:
                    print(f"[FAIL] Options is not valid JSON: {e}")

            # Test PNG conversion logic
            print("Testing PNG conversion logic...")
            needs_conversion = 'quickchart.io/chart' in decoded_url and 'format=png' not in decoded_url
            print(f"Needs PNG conversion: {needs_conversion}")

            if needs_conversion:
                # Add PNG format parameter
                if '?' in decoded_url:
                    png_url = decoded_url + '&format=png'
                else:
                    png_url = decoded_url + '?format=png'
                print(f"PNG URL: {png_url}")

        except Exception as e:
            print(f"[ERROR] Error processing URL: {e}")
    else:
        print("[FAIL] Pattern DOES NOT MATCH!")

    print()
    print("=" * 50)

    # Test the decodeUrlIfNeeded function equivalent
    print("Testing decodeUrlIfNeeded function equivalent...")

    # Python version
    def decode_url_if_needed_py(url):
        if '%' in url and re.search(r'%[0-9A-Fa-f]{2}', url):
            try:
                return urllib.parse.unquote(url)
            except:
                return url
        return url

    test_url = match[2] if match else n8n_output
    decoded = decode_url_if_needed_py(test_url)
    print(f"Original: {test_url[:100]}...")
    print(f"Decoded:  {decoded[:100]}...")

    print()
    print("Analysis Summary:")
    print("=" * 30)
    print("1. Format: Markdown image syntax with QuickChart URL")
    print("2. URL structure: Uses individual parameters (type, data, options) instead of single 'c' parameter")
    print("3. Data encoding: JSON parameters are URL-encoded")
    print("4. PNG format: Missing 'format=png' parameter")
    print("5. Compatibility: Should be detected by current chartRenderer.tsx")

if __name__ == "__main__":
    analyze_n8n_output()