#!/usr/bin/env python3
"""
Simple weather checker utility for OpenClaw.

Fetches current weather and forecasts for any location using wttr.in.
"""

import sys
import argparse
import urllib.request
import json

def get_weather(location="", format="text"):
    """Get weather information for a location."""
    if not location:
        # Try to get location from IP
        url = "https://wttr.in/?format=j1"
    else:
        url = f"https://wttr.in/{location}?format=j1"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None

def display_weather(data, location="", format="text"):
    """Display weather information."""
    if format == "json":
        print(json.dumps(data, indent=2))
        return
    
    if not data:
        print("No weather data available")
        return
    
    current = data.get('current_condition', [{}])[0]
    location_info = data.get('nearest_area', [{}])[0]
    
    area_name = location_info.get('areaName', [{}])[0].get('value', 'Unknown')
    region = location_info.get('region', [{}])[0].get('value', '')
    country = location_info.get('country', [{}])[0].get('value', '')
    
    print(f"Weather for {area_name}, {region}, {country}")
    print("=" * 40)
    print(f"Temperature: {current.get('temp_C', 'N/A')}°C ({current.get('temp_F', 'N/A')}°F)")
    print(f"Feels like: {current.get('FeelsLikeC', 'N/A')}°C ({current.get('FeelsLikeF', 'N/A')}°F)")
    print(f"Humidity: {current.get('humidity', 'N/A')}%")
    print(f"Wind: {current.get('windspeedKmph', 'N/A')} km/h {current.get('winddir16Point', 'N/A')}")
    print(f"Condition: {current.get('weatherDesc', [{}])[0].get('value', 'N/A')}")
    print(f"Pressure: {current.get('pressure', 'N/A')} mb")
    print(f"Visibility: {current.get('visibility', 'N/A')} km")
    print(f"Cloud cover: {current.get('cloudcover', 'N/A')}%")

def main():
    parser = argparse.ArgumentParser(description="Check weather for any location")
    parser.add_argument("location", nargs="?", help="Location to check (city, zip code, etc.)")
    parser.add_argument("-f", "--format", choices=["text", "json"], default="text",
                       help="Output format (default: text)")
    
    args = parser.parse_args()
    
    data = get_weather(args.location or "")
    display_weather(data, args.location, args.format)

if __name__ == "__main__":
    main()