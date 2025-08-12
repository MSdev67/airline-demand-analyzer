import pandas as pd
import numpy as np
from datetime import datetime

class DataProcessor:
    @staticmethod
    def clean_flight_data(df):
        """Clean and process flight data"""
        if df.empty:
            return df
            
        # Convert date columns
        df['date'] = pd.to_datetime(df['date'])
        df['scraped_at'] = pd.to_datetime(df['scraped_at'])
        
        # Extract day of week and month
        df['day_of_week'] = df['date'].dt.day_name()
        df['month'] = df['date'].dt.month_name()
        
        # Calculate price percentiles
        df['price_percentile'] = df.groupby(['origin', 'destination'])['price'].rank(pct=True)
        
        return df
        
    @staticmethod
    def analyze_trends(df):
        """Analyze trends from flight data"""
        if df.empty:
            return {}
            
        analysis = {}
        
        # Popular routes
        popular_routes = df.groupby(['origin', 'destination']).size().nlargest(5)
        analysis['popular_routes'] = popular_routes.to_dict()
        
        # Price trends
        price_trends = df.groupby('date')['price'].mean()
        analysis['price_trends'] = price_trends.to_dict()
        
        # Cheapest airlines
        cheapest_airlines = df.groupby('airline')['price'].mean().nsmallest(5)
        analysis['cheapest_airlines'] = cheapest_airlines.to_dict()
        
        # High demand periods
        demand_by_day = df['day_of_week'].value_counts(normalize=True)
        analysis['demand_by_day'] = demand_by_day.to_dict()
        
        demand_by_month = df['month'].value_counts(normalize=True)
        analysis['demand_by_month'] = demand_by_month.to_dict()
        
        return analysis