import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask config
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    
    # Database config
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../assets/airline_data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    AVIATIONSTACK_API_KEY = os.getenv('AVIATIONSTACK_API_KEY')  # Free tier available
    
    # Scraping config
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    SCRAPE_INTERVAL = 86400  # 24 hours in seconds