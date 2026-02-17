# import os
# import json
# import requests
# from fastapi import FastAPI
# from fastapi.responses import StreamingResponse
# from retriever import load_data

# app = FastAPI()

# OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
# MODEL_NAME = os.getenv("MODEL_NAME", "llama3")

# @app.get("/")
# def read_root():
#     return {"status": f"Chatbot API running with {MODEL_NAME}"}

# @app.get("/ask")
# def ask(query: str):
#     # Load data from latest.json
#     data = load_data() 

#     # Optimized System Prompt for Llama 3
#     optimized_prompt = f"""
#     <|begin_of_text|><|start_header_id|>system<|end_header_id|>
#     You are a professional Data Center Infrastructure Management (DCIM) Assistant. 
#     Use the following JSON data to provide accurate, concise answers. 
#     If the information is not in the data, state that you don't know.

#     DATA:
#     {json.dumps(data)}
#     <|eot_id|><|start_header_id|>user<|end_header_id|>
#     {query}
#     <|eot_id|><|start_header_id|>assistant<|end_header_id|>
#     """

#     try:
#         def generate_answer():
#             with requests.post(
#                 f"{OLLAMA_URL}/api/generate", 
#                 json={
#                     "model": MODEL_NAME,
#                     "prompt": optimized_prompt,
#                     "stream": True,
#                     "options": {
#                         "num_ctx": 4096,   # Increased for 8B model and larger data
#                         "temperature": 0.2, # Lower temperature for factual accuracy
#                         "num_thread": 8     # Optimized for modern multi-core machines
#                     }
#                 },
#                 stream=True,
#                 timeout=180
#             ) as r:
#                 for line in r.iter_lines():
#                     if line:
#                         chunk = json.loads(line)
#                         yield chunk.get("response", "")
#                         if chunk.get("done"):
#                             break

#         return StreamingResponse(generate_answer(), media_type="text/plain")

#     except Exception as e:
#         return {"answer": f"System error: {str(e)}"}


import os
import json
import requests
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from retriever import load_data

app = FastAPI()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")

@app.get("/")
def read_root():
    return {"status": f"Chatbot API running with {MODEL_NAME} on Static Data"}

@app.get("/ask")
def ask(query: str):
    # 1. Load the full historical data
    full_data = load_data()
    
    # 2. Minify JSON to save tokens (removes indentation)
    data_str = json.dumps(full_data, separators=(',', ':'))

    # 3. Construct the Llama 3 Prompt
    # We explicitly tell the model the 'Current Date' is Feb 2026 based on the data.
    optimized_prompt = f"""
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are an expert Data Center Assistant. You have access to the following monthly historical data.

**CRITICAL CONTEXT:**
- **Current Date:** Tuesday, February 17, 2026.
- **"Last Month"** refers to January 2026.
- **"Last 6 Months"** refers to Sep 2025 through Feb 2026.

**DATA STRUCTURE GUIDE:**
1. **IT Load:** Look for the key `"TenentIT"` -> `"Value"` inside each month.
2. **PMS / BMS / OutBoundAPI:** Look for `"OperationalStatus"` (0 usually means Nominal/Good, 1 means Warning/Issue, depending on site logic, but usually 0=OK).
3. **Fuel:** Look for `"FuelSupply"`. Generator names often contain `"FUEL-GEN"`.
   - To count generators > 80%, check `"CurrentLevelPercentage"`.
   - Capacity is found in `"AssetCapacityLiters"`.

**DATASET:**
{data_str}

<|eot_id|><|start_header_id|>user<|end_header_id|>
{query}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""

    try:
        def generate_answer():
            # Stream the response from Ollama
            with requests.post(
                f"{OLLAMA_URL}/api/generate", 
                json={
                    "model": MODEL_NAME,
                    "prompt": optimized_prompt,
                    "stream": True,
                    "options": {
                        "num_ctx": 8192,   # Expanded to 8k for the large JSON history
                        "temperature": 0.1, # Very low temp for strict data analysis
                        "num_thread": 8
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