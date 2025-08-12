import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import json
from config import Config

class DataScraper:
    def __init__(self):
        self.headers = {'User-Agent': Config.USER_AGENT}
        
    def scrape_flight_prices(self, origin, destination, date):
        """Scrape flight prices from Kayak (example)"""
        url = f"https://www.kayak.com/flights/{origin}-{destination}/{date}"
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'lxml')
            
            # These selectors are hypothetical - real implementation would need adjustment
            flights = soup.select('.flight-result')
            data = []
            
            for flight in flights[:10]:  # Limit to 10 results
                airline = flight.select_one('.airline-name').text.strip()
                price = flight.select_one('.price-text').text.strip()
                departure = flight.select_one('.depart-time').text.strip()
                arrival = flight.select_one('.arrival-time').text.strip()
                duration = flight.select_one('.duration').text.strip()
                
                data.append({
                    'airline': airline,
                    'price': float(price.replace('$', '').replace(',', '')),
                    'departure_time': departure,
                    'arrival_time': arrival,
                    'duration': duration,
                    'origin': origin,
                    'destination': destination,
                    'date': date,
                    'scraped_at': datetime.now().isoformat()
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            print(f"Error scraping flight prices: {e}")
            return pd.DataFrame()

    def get_aviationstack_data(self, params):
        """Get data from AviationStack API"""
        base_url = "http://api.aviationstack.com/v1/"
        params['access_key'] = Config.AVIATIONSTACK_API_KEY
        
        try:
            response = requests.get(base_url + "flights", params=params)
            data = response.json()
            
            if data.get('data'):
                return pd.DataFrame(data['data'])
            return pd.DataFrame()
            
        except Exception as e:
            print(f"Error getting AviationStack data: {e}")
            return pd.DataFrame()