import openai
from config import Config
import json

class APIHandler:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        
    def get_ai_insights(self, data, question=None):
        """Get AI-generated insights from the data"""
        try:
            prompt = f"""
            You are an airline industry analyst. Analyze this flight data and provide insights:
            {json.dumps(data, indent=2)}
            
            Focus on:
            - Demand trends
            - Pricing patterns
            - Popular routes
            - Seasonal variations
            - Recommendations for hostel businesses near airports
            
            {f"Specifically answer this question: {question}" if question else ""}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful airline industry analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message['content']
            
        except Exception as e:
            print(f"Error getting AI insights: {e}")
            return "Unable to generate insights at this time."