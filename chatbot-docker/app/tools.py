# app/tools.py
def run_tool(action, data):
    name = action.get("action")
    params = action.get("parameters", {})

    if name == "list_sites":
        return [s["siteName"] for s in data.get("map", [])] # Use .get()

    if name == "get_mw_usage":
        site = params.get("site", "")
        for s in data.get("map", []): # Use .get()
            if site.lower() in s["siteName"].lower():
                return {
                    "siteName": s["siteName"],
                    "mwUsage": s["mwUsage"],
                    "maxMw": s["maxMw"]
                }
        return {"error": "Site not found"}

    if name == "active_sites":
        return data.get("active_sites", []) # Safer access

    if name == "dashboard_summary":
        return data.get("dashboard_summary", {}) # Safer access

    return {"error": "Unknown action"}