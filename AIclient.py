# AIclient.py
import requests

def generate_health_advice(condition, food, role):
    # Use a system-style prompt to keep the AI focused
    prompt = f"""<|system|>
You are a professional nutrition assistant. Provide health advice based ONLY on the provided context.
<|user|>
The user has the following conditions: {condition}.
Our database recommends they prioritize these foods: {food}.

Provide a concise summary (max 100 words) on what to avoid and prioritize for these conditions. 
Include one helpful piece of advice. Do not include any technical instructions or meta-talk.
<|assistant|>
    """
    response = requests.post('http://localhost:11434/api/generate', 
                             json={
                                 "model": "phi3",
                                 "prompt": prompt,
                                 "stream": False,
                                 "options": {
                                     "stop": ["<|end|>", "\n#", "##"], # Prevents prompt leakage
                                     "temperature": 0.3 # Lower temperature = less "hallucination"
                                 }
                             })
    return response.json().get('response').strip()
