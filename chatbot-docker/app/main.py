import os
import json
import requests
import re
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from retriever import load_data
from tools import run_tool

app = FastAPI()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")

# Strict prompt to reduce "simulated" responses from the model
SYSTEM_PROMPT = """
You are a DCIM Assistant. You must ONLY output a JSON command to use a tool. 
Do not explain your thoughts. Do not simulate data.

Valid JSON format:
{"action": "tool_name", "parameters": {"param_name": "value"}}

Available actions:
1. list_sites: List all site names.
2. active_sites: Get the count of active sites.
3. dashboard_summary: Get general metrics (capacity, load).
4. get_mw_usage: Get power usage for a specific site. Needs 'site' parameter.
"""

def clean_json_response(raw_text):
    """
    Extracts JSON from markdown blocks or extra text added by the LLM.
    """
    # Try to find content between { and }
    match = re.search(r'(\{.*\})', raw_text, re.DOTALL)
    if match:
        return match.group(1)
    return raw_text

@app.get("/")
def read_root():
    return {"status": "Chatbot API is running"}

@app.get("/ask")
def ask(query: str):
    # Load all data immediately
    data = load_data() 
    target_model = "phi3"

    # Inject the actual data directly into the prompt to skip the "tool choice" step
    # This removes one entire 3-minute wait cycle
    optimized_prompt = f"""
    You are a DCIM Assistant. Use the provided Data Center JSON to answer the user.
    
    DATA CENTER DATA:
    {json.dumps(data, indent=1)}
    
    USER QUESTION: {query}
    
    Answer clearly and concisely based ONLY on the data above:
    """

    try:
        # Single LLM call with streaming for faster "perceived" speed
        def generate_answer():
            with requests.post(
                f"{OLLAMA_URL}/api/generate", 
                json={
                    "model": target_model,
                    "prompt": optimized_prompt,
                    "stream": True,
                    "options": {
                        "num_ctx": 2048,  # Keep context small for the i3 CPU
                        "num_thread": 4   # Match your 4 logical cores
                    }
                },
                stream=True,
                timeout=180
            ) as r:
                for line in r.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        yield chunk.get("response", "")
                        if chunk.get("done"):
                            break

        return StreamingResponse(generate_answer(), media_type="text/plain")

    except Exception as e:
        return {"answer": f"System error: {str(e)}"}