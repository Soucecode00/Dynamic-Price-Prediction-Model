# 🚗 Uber-Style Real-Time Price Prediction Application

A comprehensive real-time price prediction system for ride-sharing companies, featuring machine learning models, dynamic pricing, and real-time market monitoring.

## 🌟 Features

### Core Functionality
- **Real-Time Price Prediction**: ML-powered price estimation based on distance, time, and market conditions
- **Dynamic Pricing**: Surge pricing based on demand/supply ratios
- **Interactive Map**: Visual route selection with real-time price updates
- **WebSocket Integration**: Real-time market data streaming
- **Multiple Ride Types**: Economy, Comfort, Premium, and Luxury options

### Analytics & Monitoring
- **Real-Time Dashboard**: Live market monitoring with Streamlit
- **Price Analytics**: Distribution analysis and trend visualization
- **Market Analysis**: Demand/supply simulation and efficiency metrics
- **API Testing Interface**: Comprehensive API testing tools

### Technical Features
- **Machine Learning Model**: Random Forest regression for price prediction
- **Real-Time Updates**: WebSocket-based live data streaming
- **RESTful API**: Complete API with documentation
- **Responsive UI**: Modern, mobile-friendly interface
- **Data Visualization**: Interactive charts and graphs

## 🏗️ Architecture

```
├── app.py                 # Main FastAPI application
├── dashboard.py           # Streamlit analytics dashboard
├── static/
│   └── index.html        # Web interface
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Main Application
```bash
python app.py
```
The web interface will be available at: http://localhost:8000

### 3. Start the Analytics Dashboard (Optional)
```bash
streamlit run dashboard.py
```
The dashboard will be available at: http://localhost:8501

## 📊 Application Components

### 1. Main Web Interface (`http://localhost:8000`)
- Interactive map for route selection
- Real-time price calculation
- Live market status updates
- Beautiful, responsive design

### 2. Analytics Dashboard (`http://localhost:8501`)
- **Real-Time Monitoring**: Live market data with auto-refresh
- **Price Analytics**: Distribution analysis and trend visualization
- **Market Analysis**: Demand/supply simulation tools
- **API Testing**: Comprehensive API testing interface

## 🔌 API Endpoints

### Core Endpoints
- `GET /` - Main web interface
- `POST /predict-price` - Predict ride price
- `GET /api/market-status` - Get current market status
- `POST /api/update-demand` - Update demand factor
- `POST /api/update-supply` - Update supply factor
- `WS /ws` - WebSocket for real-time updates

### Example API Usage
```python
import requests

# Predict price
response = requests.post('http://localhost:8000/predict-price', json={
    "pickup_lat": 40.7589,
    "pickup_lng": -73.9851,
    "dropoff_lat": 40.7484,
    "dropoff_lng": -73.9857,
    "ride_type": "economy"
})

print(response.json())
```

## 🧠 Machine Learning Model

### Features Used
- Distance between pickup and dropoff
- Time of day (peak hours, late night)
- Day of week (weekend vs weekday)
- Market demand and supply factors

### Model Details
- **Algorithm**: Random Forest Regressor
- **Training Data**: Synthetic data simulating NYC area
- **Features**: 6 engineered features
- **Performance**: Realistic price predictions with surge pricing

## 🎮 Usage Examples

### 1. Basic Price Prediction
1. Open http://localhost:8000
2. Enter pickup and dropoff coordinates
3. Select ride type
4. Click "Calculate Price"
5. View real-time price with surge multiplier

### 2. Market Simulation
1. Open the dashboard at http://localhost:8501
2. Go to "Market Analysis"
3. Adjust demand and supply sliders
4. Observe real-time price changes

### 3. Analytics
1. In the dashboard, go to "Price Analytics"
2. Generate sample data
3. Explore price distributions and trends
4. Analyze surge multiplier patterns

## 🔧 Configuration

### Environment Variables
- `PORT`: Server port (default: 8000)
- `HOST`: Server host (default: 0.0.0.0)

### Customization
- Modify base prices in `app.py` (line 30)
- Adjust surge multiplier calculation in `app.py` (line 180)
- Customize ML model parameters in `PricePredictor` class

## 📈 Real-Time Features

### WebSocket Updates
- Market status updates every 5 seconds
- Automatic demand/supply fluctuations
- Real-time surge multiplier calculation

### Live Monitoring
- Current demand and supply levels
- Surge multiplier tracking
- Market efficiency metrics
- Price volatility analysis

## 🛠️ Development

### Project Structure
```
├── app.py                 # FastAPI backend
├── dashboard.py           # Streamlit frontend
├── static/               # Static files
│   └── index.html       # Web interface
├── requirements.txt      # Dependencies
├── notebook/            # Jupyter notebooks
├── images/              # Visualizations
└── README.md           # Documentation
```

### Adding New Features
1. **New ML Models**: Extend the `PricePredictor` class
2. **Additional Endpoints**: Add new routes in `app.py`
3. **UI Enhancements**: Modify `static/index.html`
4. **Analytics**: Add new pages to `dashboard.py`

## 🧪 Testing

### Manual Testing
1. Start the application
2. Test price predictions with different coordinates
3. Verify real-time updates in the dashboard
4. Test API endpoints using the testing interface

### API Testing
```bash
# Test price prediction
curl -X POST http://localhost:8000/predict-price \
  -H "Content-Type: application/json" \
  -d '{"pickup_lat": 40.7589, "pickup_lng": -73.9851, "dropoff_lat": 40.7484, "dropoff_lng": -73.9857}'

# Get market status
curl http://localhost:8000/api/market-status
```

## 🚨 Troubleshooting

### Common Issues
1. **Port already in use**: Change port in `app.py`
2. **Dependencies missing**: Run `pip install -r requirements.txt`
3. **WebSocket connection failed**: Check if server is running
4. **Map not loading**: Check internet connection for OpenStreetMap

### Debug Mode
```bash
# Run with debug logging
python -u app.py
```

## 📊 Performance

### Current Capabilities
- **Response Time**: < 100ms for price predictions
- **Concurrent Users**: Supports multiple simultaneous connections
- **Real-Time Updates**: 5-second refresh intervals
- **Data Points**: 1000+ synthetic training samples

### Scalability
- Stateless API design
- Efficient ML model inference
- WebSocket connection pooling
- Responsive UI with minimal server load

## 🔮 Future Enhancements

### Planned Features
- **Geolocation API**: Automatic location detection
- **Traffic Integration**: Real-time traffic data
- **Weather Impact**: Weather-based pricing adjustments
- **User Authentication**: Multi-user support
- **Database Integration**: Persistent data storage
- **Advanced ML**: Deep learning models

### Potential Integrations
- **Google Maps API**: Enhanced routing
- **Weather APIs**: Weather-based pricing
- **Payment Gateways**: Direct payment processing
- **Mobile Apps**: Native mobile applications

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For questions or support:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

---

**Built with ❤️ using FastAPI, Streamlit, and Machine Learning**

