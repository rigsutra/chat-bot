import json

DATA_FILE = "data/latest.json"


def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def get_site_mw_usage(site_keyword: str):
    data = load_data()

    for site in data.get("map", []):
        if site_keyword.lower() in site["siteName"].lower():
            return {
                "siteName": site["siteName"],
                "mwUsage": site["mwUsage"],
                "maxMw": site["maxMw"]
            }

    return None