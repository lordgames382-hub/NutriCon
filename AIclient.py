# AIclient.py
import os
import requests

def generate_health_advice(condition, food, role):
    # Retrieve the API key from Render's secure environment variables
    # Locally, it will fall back to look for an environment variable on your PC
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return "Error: AI configuration missing. Please set the GEMINI_API_KEY environment variable."

    # Gemini's API text generation endpoint
    # Using the current active stable production model alias
    # The correct active endpoint path for Gemini 1.5 Flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # Reconstructing your exact prompt structure
    prompt = f"""You are a professional nutrition assistant. Provide health advice based ONLY on the provided context.

The user has the following conditions: {condition}.
Our database recommends they prioritize these foods: {food}.

Provide a concise summary (max 100 words) on what to avoid and prioritize for these conditions. 
Include one helpful piece of advice. Do not include any technical instructions or meta-talk."""

    # Formatting the payload exactly how the Gemini API expects it
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 200
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status() # Raise an error for bad response codes
        
        # Safely extract the text response from Gemini's JSON structure
        result_json = response.json()
        advice = result_json['candidates'][0]['content']['parts'][0]['text']
        return advice.strip()
        
    except Exception as e:
        return f"Nutrition advice temporarily unavailable. (Error: {str(e)})"