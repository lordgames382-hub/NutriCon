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
    # An updated, flexible prompt that doesn't choke on missing database items
    prompt = f"""You are a professional nutrition assistant. 

The user has been diagnosed with the following health conditions: {condition}.
Our database recommends prioritizing these specific foods if available: {food if food else "No specific database items listed"}.

Task:
Provide a highly concise, practical summary (maximum 100 words) outlining what a person with these conditions should prioritize in their daily diet and what major food groups they ought to avoid. 

Guidelines:
- If specific foods were provided above, incorporate them. If not, utilize your general nutritional knowledge to provide safe recommendations for the stated conditions.
- Include one actionable, helpful piece of daily advice.
- Do not include any technical instructions, introductory greetings, or meta-talk. Start speaking directly."""

    try:
        # UPDATE: Pointing to the active supported production model instead of the deprecated 1.5 versions
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generate content with options matching your old configuration
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=600
            )
        )
        
        return response.text.strip()
        
    except Exception as e:
        return f"Nutrition advice temporarily unavailable. (Error: {str(e)})"