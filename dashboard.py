import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import time
import threading

# Page configuration
st.set_page_config(
    page_title="Uber-Style Price Prediction Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stAlert {
        background-color: #e8f4fd;
        border: 1px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'price_history' not in st.session_state:
    st.session_state.price_history = []
if 'market_data' not in st.session_state:
    st.session_state.market_data = []

# API base URL
API_BASE_URL = "http://localhost:8000"

def get_market_status():
    """Get current market status from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/market-status")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def predict_price(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, ride_type="economy"):
    """Predict price using API"""
    try:
        response = requests.post(f"{API_BASE_URL}/predict-price", json={
            "pickup_lat": pickup_lat,
            "pickup_lng": pickup_lng,
            "dropoff_lat": dropoff_lat,
            "dropoff_lng": dropoff_lng,
            "ride_type": ride_type
        })
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def generate_sample_data():
    """Generate sample data for demonstration"""
    np.random.seed(42)
    
    # Generate sample coordinates around NYC
    n_samples = 100
    pickup_lats = np.random.uniform(40.7, 40.8, n_samples)
    pickup_lngs = np.random.uniform(-74.0, -73.9, n_samples)
    dropoff_lats = np.random.uniform(40.7, 40.8, n_samples)
    dropoff_lngs = np.random.uniform(-74.0, -73.9, n_samples)
    
    data = []
    for i in range(n_samples):
        price_data = predict_price(
            pickup_lats[i], pickup_lngs[i],
            dropoff_lats[i], dropoff_lngs[i]
        )
        if price_data:
            data.append({
                'timestamp': datetime.now(),
                'pickup_lat': pickup_lats[i],
                'pickup_lng': pickup_lngs[i],
                'dropoff_lat': dropoff_lats[i],
                'dropoff_lng': dropoff_lngs[i],
                'base_price': price_data['base_price'],
                'total_price': price_data['total_price'],
                'surge_multiplier': price_data['surge_multiplier'],
                'distance': price_data['estimated_distance'],
                'duration': price_data['estimated_duration'],
                'demand': price_data['demand_factor'],
                'supply': price_data['supply_factor']
            })
    
    return pd.DataFrame(data)

# Main dashboard
def main():
    st.markdown('<h1 class="main-header">🚗 Uber-Style Price Prediction Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Dashboard Controls")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Real-Time Monitoring", "Price Analytics", "Market Analysis", "API Testing"]
    )
    
    if page == "Real-Time Monitoring":
        show_realtime_monitoring()
    elif page == "Price Analytics":
        show_price_analytics()
    elif page == "Market Analysis":
        show_market_analysis()
    elif page == "API Testing":
        show_api_testing()

def show_realtime_monitoring():
    """Real-time monitoring page"""
    st.header("📊 Real-Time Market Monitoring")
    
    # Auto-refresh
    auto_refresh = st.checkbox("Enable auto-refresh (5s)", value=True)
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Get current market status
    market_status = get_market_status()
    
    if market_status:
        with col1:
            st.metric(
                label="Current Demand",
                value=f"{market_status['demand']:.2f}",
                delta=f"{market_status['demand'] - 1.0:.2f}"
            )
        
        with col2:
            st.metric(
                label="Current Supply",
                value=f"{market_status['supply']:.2f}",
                delta=f"{market_status['supply'] - 1.0:.2f}"
            )
        
        with col3:
            st.metric(
                label="Surge Multiplier",
                value=f"{market_status['surge_multiplier']:.2f}x",
                delta=f"{market_status['surge_multiplier'] - 1.0:.2f}"
            )
        
        with col4:
            st.metric(
                label="Last Updated",
                value=datetime.fromisoformat(market_status['timestamp'].replace('Z', '+00:00')).strftime('%H:%M:%S')
            )
        
        # Store market data for history
        st.session_state.market_data.append({
            'timestamp': datetime.now(),
            'demand': market_status['demand'],
            'supply': market_status['supply'],
            'surge_multiplier': market_status['surge_multiplier']
        })
        
        # Keep only last 100 data points
        if len(st.session_state.market_data) > 100:
            st.session_state.market_data = st.session_state.market_data[-100:]
        
        # Real-time charts
        st.subheader("📈 Market Trends")
        
        if len(st.session_state.market_data) > 1:
            df_market = pd.DataFrame(st.session_state.market_data)
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Demand & Supply Over Time', 'Surge Multiplier Over Time'),
                vertical_spacing=0.1
            )
            
            # Demand and Supply
            fig.add_trace(
                go.Scatter(x=df_market['timestamp'], y=df_market['demand'], 
                          name='Demand', line=dict(color='red')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df_market['timestamp'], y=df_market['supply'], 
                          name='Supply', line=dict(color='blue')),
                row=1, col=1
            )
            
            # Surge Multiplier
            fig.add_trace(
                go.Scatter(x=df_market['timestamp'], y=df_market['surge_multiplier'], 
                          name='Surge Multiplier', line=dict(color='orange')),
                row=2, col=1
            )
            
            fig.update_layout(height=600, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.error("⚠️ Unable to connect to the API server. Please make sure the server is running.")
        st.info("Start the server with: `python app.py`")

def show_price_analytics():
    """Price analytics page"""
    st.header("💰 Price Analytics")
    
    # Generate sample data
    if st.button("Generate Sample Price Data"):
        with st.spinner("Generating sample data..."):
            df = generate_sample_data()
            st.session_state.price_history = df.to_dict('records')
            st.success(f"Generated {len(df)} sample price predictions!")
    
    if st.session_state.price_history:
        df = pd.DataFrame(st.session_state.price_history)
        
        # Price distribution
        st.subheader("📊 Price Distribution")
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(df, x='total_price', nbins=20, 
                             title='Distribution of Total Prices',
                             labels={'total_price': 'Price ($)', 'count': 'Frequency'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.box(df, y='total_price', title='Price Box Plot')
            st.plotly_chart(fig, use_container_width=True)
        
        # Price vs Distance
        st.subheader("📏 Price vs Distance Analysis")
        fig = px.scatter(df, x='distance', y='total_price', 
                        color='surge_multiplier', size='duration',
                        title='Price vs Distance with Surge Multiplier',
                        labels={'distance': 'Distance (km)', 'total_price': 'Price ($)'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Surge multiplier analysis
        st.subheader("⚡ Surge Multiplier Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(df, x='surge_multiplier', nbins=15,
                             title='Surge Multiplier Distribution')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            surge_stats = df['surge_multiplier'].describe()
            st.metric("Average Surge", f"{surge_stats['mean']:.2f}x")
            st.metric("Max Surge", f"{surge_stats['max']:.2f}x")
            st.metric("Min Surge", f"{surge_stats['min']:.2f}x")
    
    else:
        st.info("Click 'Generate Sample Price Data' to see analytics.")

def show_market_analysis():
    """Market analysis page"""
    st.header("📈 Market Analysis")
    
    # Market simulation controls
    st.subheader("🎮 Market Simulation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_demand = st.slider("Demand Factor", 0.5, 2.0, 1.0, 0.1)
        if st.button("Update Demand"):
            try:
                response = requests.post(f"{API_BASE_URL}/api/update-demand", json=new_demand)
                if response.status_code == 200:
                    st.success(f"Demand updated to {new_demand}")
                else:
                    st.error("Failed to update demand")
            except:
                st.error("Unable to connect to API")
    
    with col2:
        new_supply = st.slider("Supply Factor", 0.5, 2.0, 1.0, 0.1)
        if st.button("Update Supply"):
            try:
                response = requests.post(f"{API_BASE_URL}/api/update-supply", json=new_supply)
                if response.status_code == 200:
                    st.success(f"Supply updated to {new_supply}")
                else:
                    st.error("Failed to update supply")
            except:
                st.error("Unable to connect to API")
    
    # Market efficiency metrics
    st.subheader("📊 Market Efficiency Metrics")
    
    market_status = get_market_status()
    if market_status:
        demand = market_status['demand']
        supply = market_status['supply']
        surge = market_status['surge_multiplier']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            efficiency = min(demand, supply) / max(demand, supply) * 100
            st.metric("Market Efficiency", f"{efficiency:.1f}%")
        
        with col2:
            imbalance = abs(demand - supply) / max(demand, supply) * 100
            st.metric("Market Imbalance", f"{imbalance:.1f}%")
        
        with col3:
            st.metric("Price Volatility", f"{(surge - 1.0) * 100:.1f}%")
        
        # Market state indicator
        if demand > supply * 1.2:
            st.warning("🚨 High demand - Surge pricing likely")
        elif supply > demand * 1.2:
            st.info("📉 Low demand - Prices may be lower")
        else:
            st.success("✅ Balanced market conditions")

def show_api_testing():
    """API testing page"""
    st.header("🔧 API Testing")
    
    st.subheader("Test Price Prediction")
    
    # Test coordinates
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Pickup Location**")
        pickup_lat = st.number_input("Latitude", value=40.7589, format="%.6f")
        pickup_lng = st.number_input("Longitude", value=-73.9851, format="%.6f")
    
    with col2:
        st.write("**Dropoff Location**")
        dropoff_lat = st.number_input("Latitude", value=40.7484, format="%.6f")
        dropoff_lng = st.number_input("Longitude", value=-73.9857, format="%.6f")
    
    ride_type = st.selectbox("Ride Type", ["economy", "comfort", "premium", "luxury"])
    
    if st.button("Test Price Prediction"):
        with st.spinner("Testing API..."):
            result = predict_price(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, ride_type)
            
            if result:
                st.success("✅ API call successful!")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Base Price", f"${result['base_price']:.2f}")
                
                with col2:
                    st.metric("Total Price", f"${result['total_price']:.2f}")
                
                with col3:
                    st.metric("Surge Multiplier", f"{result['surge_multiplier']:.2f}x")
                
                with col4:
                    st.metric("Distance", f"{result['estimated_distance']:.2f} km")
                
                # Show full response
                with st.expander("Full API Response"):
                    st.json(result)
            else:
                st.error("❌ API call failed!")
    
    # API endpoints info
    st.subheader("📋 Available API Endpoints")
    
    endpoints = [
        {"Method": "GET", "Endpoint": "/", "Description": "Main web interface"},
        {"Method": "POST", "Endpoint": "/predict-price", "Description": "Predict ride price"},
        {"Method": "GET", "Endpoint": "/api/market-status", "Description": "Get market status"},
        {"Method": "POST", "Endpoint": "/api/update-demand", "Description": "Update demand factor"},
        {"Method": "POST", "Endpoint": "/api/update-supply", "Description": "Update supply factor"},
        {"Method": "WS", "Endpoint": "/ws", "Description": "WebSocket for real-time updates"}
    ]
    
    st.table(pd.DataFrame(endpoints))

if __name__ == "__main__":
    main()