# import json

# DATA_FILE = "data/latest.json"


# def load_data():
#     with open(DATA_FILE, "r") as f:
#         return json.load(f)


# def get_site_mw_usage(site_keyword: str):
#     data = load_data()

#     for site in data.get("map", []):
#         if site_keyword.lower() in site["siteName"].lower():
#             return {
#                 "siteName": site["siteName"],
#                 "mwUsage": site["mwUsage"],
#                 "maxMw": site["maxMw"]
#             }

#     return None

import json
import os

# Updated to point to the new static file
DATA_FILE = "data/historical_data.json"

def load_data():
    """
    Loads the static historical data from the JSON file.
    """
    try:
        if not os.path.exists(DATA_FILE):
            print(f"Error: {DATA_FILE} not found.")
            return {}
            
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return {}