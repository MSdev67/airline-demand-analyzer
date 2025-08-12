from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from utils.data_scraper import DataScraper
from utils.data_processor import DataProcessor
from utils.api_handler import APIHandler
from config import Config
import pandas as pd
import plotly
import plotly.express as px
import json
import threading
import time
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)
db = SQLAlchemy(app)

# Database Model
class FlightData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    airline = db.Column(db.String(100))
    price = db.Column(db.Float)
    departure_time = db.Column(db.String(50))
    arrival_time = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    origin = db.Column(db.String(10))
    destination = db.Column(db.String(10))
    date = db.Column(db.DateTime)
    scraped_at = db.Column(db.DateTime)
    day_of_week = db.Column(db.String(20))
    month = db.Column(db.String(20))
    price_percentile = db.Column(db.Float)

# Initialize helpers
scraper = DataScraper()
processor = DataProcessor()
api_handler = APIHandler()

# Background task for periodic scraping
def background_scraper():
    with app.app_context():
        while True:
            print("Running background scraper...")
            try:
                # Example cities in Australia
                cities = ['SYD', 'MEL', 'BNE', 'PER', 'ADL']
                date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                
                for origin in cities:
                    for destination in cities:
                        if origin != destination:
                            df = scraper.scrape_flight_prices(origin, destination, date)
                            if not df.empty:
                                df = processor.clean_flight_data(df)
                                self.update_database(df)
                                
                # Also get data from AviationStack API
                params = {
                    'flight_date': datetime.now().strftime('%Y-%m-%d'),
                    'dep_iata': 'SYD',  # Sydney as example
                    'limit': 100
                }
                api_df = scraper.get_aviationstack_data(params)
                if not api_df.empty:
                    self.update_database(api_df)
                    
            except Exception as e:
                print(f"Error in background scraper: {e}")
                
            time.sleep(Config.SCRAPE_INTERVAL)

def update_database(df):
    """Update database with new data"""
    for _, row in df.iterrows():
        exists = FlightData.query.filter_by(
            airline=row.get('airline'),
            origin=row.get('origin'),
            destination=row.get('destination'),
            date=row.get('date'),
            departure_time=row.get('departure_time')
        ).first()
        
        if not exists:
            flight = FlightData(
                airline=row.get('airline'),
                price=row.get('price'),
                departure_time=row.get('departure_time'),
                arrival_time=row.get('arrival_time'),
                duration=row.get('duration'),
                origin=row.get('origin'),
                destination=row.get('destination'),
                date=row.get('date'),
                scraped_at=row.get('scraped_at'),
                day_of_week=row.get('day_of_week'),
                month=row.get('month'),
                price_percentile=row.get('price_percentile')
            )
            db.session.add(flight)
    
    db.session.commit()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Get form data
    origin = request.form.get('origin', 'SYD')
    destination = request.form.get('destination', 'MEL')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    # Query database
    query = FlightData.query
    
    if origin:
        query = query.filter_by(origin=origin)
    if destination:
        query = query.filter_by(destination=destination)
    if start_date:
        query = query.filter(FlightData.date >= start_date)
    if end_date:
        query = query.filter(FlightData.date <= end_date)
        
    df = pd.read_sql(query.statement, db.session.bind)
    
    if df.empty:
        return render_template('results.html', error="No data found for the selected filters.")
    
    # Process data
    df = processor.clean_flight_data(df)
    trends = processor.analyze_trends(df)
    
    # Create visualizations
    graphs = []
    
    # Price trends over time
    fig = px.line(df, x='date', y='price', color='airline', 
                  title=f'Price Trends: {origin} to {destination}')
    graphs.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    
    # Demand by day of week
    fig = px.bar(df['day_of_week'].value_counts().reset_index(), 
                 x='index', y='day_of_week',
                 title='Demand by Day of Week')
    graphs.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    
    # Price distribution
    fig = px.box(df, x='airline', y='price', title='Price Distribution by Airline')
    graphs.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    
    # Popular routes
    route_counts = df.groupby(['origin', 'destination']).size().reset_index(name='counts')
    fig = px.treemap(route_counts, path=['origin', 'destination'], values='counts',
                     title='Popular Flight Routes')
    graphs.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    
    return render_template('results.html', 
                         graphs=graphs,
                         trends=trends,
                         origin=origin,
                         destination=destination)

@app.route('/ai_assistant')
def ai_assistant():
    return render_template('ai_assistant.html')

@app.route('/get_ai_response', methods=['POST'])
def get_ai_response():
    data = request.json
    question = data.get('question')
    
    # Get some recent data to provide context
    recent_flights = FlightData.query.order_by(FlightData.scraped_at.desc()).limit(100)
    df = pd.read_sql(recent_flights.statement, db.session.bind)
    trends = processor.analyze_trends(df)
    
    response = api_handler.get_ai_insights(trends, question)
    return jsonify({'response': response})

# SocketIO events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
    # Start background scraper in a separate thread
    scraper_thread = threading.Thread(target=background_scraper)
    scraper_thread.daemon = True
    scraper_thread.start()
    
    socketio.run(app, debug=True)