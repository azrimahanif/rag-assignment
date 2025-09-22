#!/usr/bin/env python3
"""
Simple test to check the normalized URL
"""

import urllib.parse

ai_url = "https://quickchart.io/chart?width=200&c=%7B%22type%22%3A%22bar%22%2C%22data%22%3A%7B%22labels%22%3A%5B%22Selangor%22%2C%22Kedah%22%5D%2C%22datasets%22%3A%5B%7B%22label%22%3A%22Total%20Population%22%2C%22data%22%3A%5B7209.7%2C2189.3%5D%7D%5D%7D%2C%22options%22%3A%7B%22plugins%22%3A%7B%22title%22%3A%7B%22display%22%3Atrue%2C%22text%22%3A%22Population%20Comparison%20between%20Selangor%20and%20Kedah%20in%202023%22%7D%7D%7D%7D"

# Parse the URL
parsed_url = urllib.parse.urlparse(ai_url)
params = urllib.parse.parse_qs(parsed_url.query)

config_param = params.get('c', [None])[0]
width_param = params.get('width', [None])[0]

# Decode the JSON config (simulate AI agent processing)
final_config_param = urllib.parse.unquote(config_param)

# Build the normalized URL
base_url = 'https://quickchart.io/chart'
query_params = {}
query_params['format'] = 'png'

if width_param:
    query_params['width'] = width_param[0]

# Build parameters
other_params = '&'.join([f"{key}={urllib.parse.quote(str(value))}" for key, value in query_params.items()])
json_param = f"c={urllib.parse.quote(final_config_param)}"
query_string = f"{json_param}&{other_params}" if other_params else json_param
final_url = f"{base_url}?{query_string}"

print("ORIGINAL URL:")
print(ai_url)
print()

print("NORMALIZED URL:")
print(final_url)
print()

print("CHECKING:")
print(f"Has PNG: {'format=png' in final_url}")
print(f"Has width: {'width=200' in final_url or 'width=' in final_url}")
print(f"Has config: {'c=' in final_url}")

# Parse final URL to check parameters
final_parsed = urllib.parse.urlparse(final_url)
final_params = urllib.parse.parse_qs(final_parsed.query)

print("\nFINAL PARAMETERS:")
for key, value in final_params.items():
    if key == 'c':
        print(f"{key}: {value[0][:50]}...")
    else:
        print(f"{key}: {value[0]}")