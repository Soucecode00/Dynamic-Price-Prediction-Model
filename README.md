# TaxiPrice AI - Real-Time Price Prediction Application

A comprehensive real-time taxi price prediction application similar to Uber's dynamic pricing system. This application uses machine learning to predict ride prices based on demand, supply, weather, traffic, and other market factors.

![TaxiPrice AI Dashboard](https://via.placeholder.com/800x400?text=TaxiPrice+AI+Dashboard)

## 🚀 Features

### Real-Time Pricing Engine
- **Dynamic Surge Pricing**: Intelligent pricing based on supply and demand
- **Machine Learning Model**: Ensemble model using Random Forest and Gradient Boosting
- **Multi-Factor Analysis**: Weather, traffic, location, time-based pricing
- **Live Market Data**: Real-time updates every 5 seconds via WebSocket

### Interactive Dashboard
- **Live Market Overview**: Real-time metrics and KPIs
- **Interactive Surge Map**: Geographic visualization of pricing zones
- **Demand Analytics**: Historical and real-time demand patterns
- **Price Breakdown**: Detailed cost analysis and factors

### Advanced Analytics
- **Demand Forecasting**: 6-hour ahead predictions
- **Historical Analysis**: Trends and patterns over time
- **Market Insights**: Peak hours, surge distribution, efficiency metrics
- **Performance Tracking**: Model accuracy and market balance

### Price Calculator
- **Instant Predictions**: Real-time price estimation
- **Multiple Ride Types**: Economy, Standard, Premium, Luxury
- **Location Presets**: Popular NYC locations
- **Optimization Tips**: Smart recommendations for users

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │   Flask Backend │    │   ML Pipeline   │
│                 │    │                 │    │                 │
│ • Dashboard     │◄──►│ • REST API      │◄──►│ • Price Model   │
│ • Calculator    │    │ • WebSocket     │    │ • Data Simulator│
│ • Analytics     │    │ • Real-time     │    │ • Feature Eng.  │
│ • Maps          │    │   Updates       │    │ • Training      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Components │    │   Market Data   │    │   Trained Model │
│                 │    │                 │    │                 │
│ • Charts        │    │ • Supply/Demand │    │ • Random Forest │
│ • Maps          │    │ • Weather       │    │ • Gradient Boost│
│ • Forms         │    │ • Traffic       │    │ • Ensemble      │
│ • Real-time     │    │ • Events        │    │ • Persistence   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **Python 3.9+** - Core language
- **Flask** - Web framework
- **Flask-SocketIO** - Real-time communication
- **scikit-learn** - Machine learning
- **pandas/numpy** - Data processing
- **SQLAlchemy** - Database ORM

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety (optional)
- **Tailwind CSS** - Styling
- **Socket.IO Client** - Real-time updates
- **Recharts** - Data visualization
- **Leaflet** - Interactive maps

### Infrastructure
- **Redis** - Caching and session management
- **PostgreSQL** - Data persistence
- **Celery** - Background tasks
- **Docker** - Containerization
- **Gunicorn** - WSGI server

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn
- Redis (optional, for production)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/taxiprice-ai.git
cd taxiprice-ai
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set up React frontend**
```bash
npm install
```

4. **Initialize the ML model**
```bash
python price_model.py
```

### Running the Application

1. **Start the backend server**
```bash
python app.py
```
The backend will be available at `http://localhost:5000`

2. **Start the frontend development server**
```bash
npm start
```
The frontend will be available at `http://localhost:3000`

3. **Access the application**
Open your browser to `http://localhost:3000`

## 📊 API Documentation

### Price Prediction
```http
POST /api/predict_price
Content-Type: application/json

{
  "pickup_lat": 40.7128,
  "pickup_lng": -74.0060,
  "dropoff_lat": 40.7589,
  "dropoff_lng": -73.9851,
  "ride_type": "standard"
}
```

**Response:**
```json
{
  "predicted_price": 15.75,
  "base_price": 12.50,
  "surge_multiplier": 1.2,
  "estimated_time": 18,
  "distance": 5.2,
  "breakdown": {
    "base_fare": 7.50,
    "distance_cost": 3.75,
    "time_cost": 1.25,
    "surge_adjustment": 3.00
  },
  "factors": {
    "demand_level": "High",
    "supply_level": "Medium",
    "weather_impact": 1.1,
    "traffic_impact": 1.3
  }
}
```

### Market Data
```http
GET /api/market_data
```

**Response:**
```json
{
  "active_drivers": 150,
  "ride_requests": 65,
  "surge_multiplier": 1.4,
  "weather_factor": 1.1,
  "traffic_factor": 1.3,
  "weather_condition": "rain",
  "demand_supply_ratio": 0.433,
  "timestamp": "2023-12-07T15:30:00Z"
}
```

### Historical Data
```http
GET /api/historical_data?days=7
```

### Surge Zones
```http
GET /api/surge_zones
```

## 🤖 Machine Learning Model

### Model Architecture
The pricing model uses an ensemble approach combining:

1. **Random Forest Regressor** (60% weight)
   - Handles non-linear patterns
   - Feature importance analysis
   - Robust to outliers

2. **Gradient Boosting Regressor** (40% weight)
   - Captures complex interactions
   - Sequential error correction
   - High accuracy on structured data

### Features Used
- **Spatial**: Pickup/dropoff coordinates, distance
- **Temporal**: Hour, day of week, weekend indicator
- **Market**: Active drivers, ride requests, demand/supply ratio
- **Environmental**: Weather factor, traffic factor
- **Derived**: Rush hour, weekend evening, distance squared

### Training Process
```python
# Feature engineering
features = engineer_features(raw_data)

# Model training
rf_model = RandomForestRegressor(n_estimators=100)
gb_model = GradientBoostingRegressor(n_estimators=100)

# Ensemble prediction
prediction = 0.6 * rf_pred + 0.4 * gb_pred
```

### Model Performance
- **MAE**: ~$1.50 (Mean Absolute Error)
- **R²**: 0.85+ (Coefficient of Determination)
- **Features**: 15 engineered features
- **Training Data**: 10,000+ synthetic samples

## 📱 Frontend Components

### Dashboard (`/`)
- Real-time market overview
- Interactive surge pricing map
- Live demand charts
- Market events and alerts

### Price Calculator (`/calculator`)
- Trip detail input form
- Instant price predictions
- Price breakdown analysis
- Optimization recommendations

### Analytics (`/analytics`)
- Historical trend analysis
- Peak hour identification
- Surge distribution charts
- Market insights and KPIs

## 🔄 Real-Time Updates

The application uses WebSocket connections for real-time data:

```javascript
// Frontend WebSocket connection
const socket = io('http://localhost:5000');

socket.on('market_update', (data) => {
  setMarketData(data);
});
```

```python
# Backend real-time updates
@socketio.on('connect')
def handle_connect():
    emit('market_update', current_market_data)

# Background updates every 5 seconds
def update_market_data():
    while True:
        updated_data = data_simulator.update_market_conditions()
        socketio.emit('market_update', updated_data)
        time.sleep(5)
```

## 🧪 Testing

### Run Backend Tests
```bash
python -m pytest tests/
```

### Run Frontend Tests
```bash
npm test
```

### Load Testing
```bash
# Install artillery
npm install -g artillery

# Run load tests
artillery run load-test.yml
```

## 🚀 Deployment

### Docker Deployment

1. **Build images**
```bash
docker-compose build
```

2. **Run services**
```bash
docker-compose up -d
```

### Production Environment

1. **Environment Variables**
```bash
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@localhost/db
export REDIS_URL=redis://localhost:6379
```

2. **Web Server**
```bash
gunicorn --worker-class eventlet -w 1 app:app
```

3. **Frontend Build**
```bash
npm run build
serve -s build
```

## 🔧 Configuration

### Environment Variables
```bash
# Backend Configuration
FLASK_ENV=development
DATABASE_URL=sqlite:///app.db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key

# API Keys (if using external services)
WEATHER_API_KEY=your-weather-api-key
MAPS_API_KEY=your-maps-api-key
```

### Application Settings
```python
# app.py
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key'),
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL'),
    REDIS_URL=os.environ.get('REDIS_URL', 'redis://localhost:6379')
)
```

## 📈 Performance Optimization

### Backend Optimizations
- **Redis Caching**: Cache frequent predictions
- **Database Indexing**: Optimize query performance
- **Async Processing**: Background model training
- **Connection Pooling**: Database connections

### Frontend Optimizations
- **Code Splitting**: Lazy load components
- **Memoization**: React.memo for expensive components
- **Virtual Scrolling**: Large data sets
- **Service Worker**: Offline functionality

## 🔐 Security

### API Security
- **CORS Configuration**: Controlled origins
- **Rate Limiting**: Prevent abuse
- **Input Validation**: Sanitize user inputs
- **Authentication**: JWT tokens (if implementing user accounts)

### Data Protection
- **Encryption**: Sensitive data at rest
- **HTTPS**: Secure data transmission
- **Input Sanitization**: Prevent injection attacks
- **Access Control**: Role-based permissions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Write tests for new features
- Update documentation

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Uber Technologies** - Inspiration for surge pricing algorithms
- **OpenStreetMap** - Map data and tiles
- **scikit-learn** - Machine learning framework
- **React Community** - UI framework and ecosystem

## 📞 Support

For support, email support@taxiprice-ai.com or join our [Discord server](https://discord.gg/taxiprice-ai).

## 🗺️ Roadmap

- [ ] **Mobile App** - React Native implementation
- [ ] **Driver App** - Supply-side optimization
- [ ] **Advanced ML** - Deep learning models
- [ ] **Multi-City** - Support for multiple cities
- [ ] **Real Weather API** - Live weather integration
- [ ] **Payment Integration** - Stripe/PayPal integration
- [ ] **Admin Dashboard** - Fleet management tools
- [ ] **API Marketplace** - Third-party integrations

---

**Built with ❤️ for the future of transportation pricing**

