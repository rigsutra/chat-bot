import os
import time
import json
import requests
from dotenv import load_dotenv

# Load .env file for local development outside of Docker
load_dotenv()

# Environment variables from .env
LOGIN_URL = os.getenv("LOGIN_URL")
USERNAME = os.getenv("USERNAME")
SITENAME = os.getenv("SITENAME", "") 
AUTH_TOKEN = os.getenv("AUTH_TOKEN") 

# API Endpoints
APIS = {
    "dashboard_summary": "https://global-dev-api.yondrone.com/api/widget-global/dashboard-widget-summary",
    "active_sites": "https://global-dev-api.yondrone.com/api/widget-global/active-site",
    "map": "https://global-dev-api.yondrone.com/api/widget-global/map",
    "sites": "https://global-dev-api.yondrone.com/api/site/sites",
}

# Determine output path based on environment
if os.path.exists("/data"):
    OUTPUT_FILE = "/data/latest.json"
else:
    OUTPUT_FILE = "latest.json"


def login():
    """
    Handles authentication using automated login or manual token fallback.
    """
    if AUTH_TOKEN:
        print("Using manually provided AUTH_TOKEN from .env.")
        return AUTH_TOKEN

    print(f"Attempting automated login for {USERNAME} at {LOGIN_URL}...")
    
    payload = {
        "userName": USERNAME,
        "siteName": SITENAME
    }

    try:
        response = requests.post(LOGIN_URL, json=payload)
        print(f"Login API Response: {response.status_code} - {response.text}")

        if response.status_code != 200:
            return None

        token = response.json().get("token")
        return token
    except Exception as e:
        print(f"Login request error: {e}")
        return None


def fetch_all(token):
    """
    Fetches data with detailed debug prints. 
    Uses POST for 'sites' and GET for others.
    """
    clean_token = token.replace("Bearer ", "").strip()
    
    headers = {
        "Authorization": f"Bearer {clean_token}",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Origin": "https://global-dev-api.yondrone.com",
        "Referer": "https://global-dev-api.yondrone.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site"
    }

    # Specific payload for the sites POST API
    sites_payload = {
        "siteName": "",
        "pageNumber": 1,
        "pageSize": 1000,
        "sortOrder": "",
        "sortColumn": "",
        "searchQuery": ""
    }

    result = {}

    for name, url in APIS.items():
        print(f"\n--- Fetching: {name} ---")
        print(f"URL: {url}")

        try:
            # Determine method and payload
            if name == "sites":
                print("Method: POST")
                r = requests.post(url, headers=headers, json=sites_payload)
            else:
                print("Method: GET")
                r = requests.get(url, headers=headers)
            
            # Debugging prints for each response
            print(f"Status Code: {r.status_code}")
            print(f"Raw Response (first 500 chars): {r.text[:500]}")

            if r.status_code == 200:
                result[name] = r.json()
                print(f"Successfully parsed {name} data.")
            else:
                print(f"Failed to fetch {name}. Check authorization or payload requirements.")

        except Exception as e:
            print(f"Error during fetch of {name}: {e}")

    return result


def save(data):
    """
    Saves fetched data to latest.json.
    """
    if not data:
        print("\nNo data fetched this cycle. Skipping save.")
        return

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\nData updated successfully in {OUTPUT_FILE}.")


def main():
    """
    Main loop for scheduled data fetching.
    """
    while True:
        try:
            token = login()
            if token:
                data = fetch_all(token)
                save(data)
            else:
                print("Token unavailable. Fetch skipped.")

        except Exception as e:
            print("Execution error:", e)

        print("\nSleeping for 10 minutes...")
        time.sleep(600)


if __name__ == "__main__":
    main()