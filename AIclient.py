# AIclient.py
import os
import google.generativeai as genai

def generate_health_advice(condition, food, role):
    # Fetch key from Render's Environment Variables
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return "Error: AI configuration missing. Please set the GEMINI_API_KEY environment variable."
    
    # Configure the official SDK with your key
    genai.configure(api_key=api_key)
    
    # Reconstruct your prompt exactly
    prompt = f"""You are a professional nutrition assistant. Provide health advice based ONLY on the provided context.

The user has the following conditions: {condition}.
Our database recommends they prioritize these foods: {food}.

Provide a concise summary (max 100 words) on what to avoid and prioritize for these conditions. 
Include one helpful piece of advice. Do not include any technical instructions or meta-talk."""

    try:
        # FIX: Added the explicit 'models/' prefix required by the backend API registry
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        # Generate content with your custom configurations
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=200
            )
        )
        
        return response.text.strip()
        
    except Exception as e:
        return f"Nutrition advice temporarily unavailable. (Error: {str(e)})"