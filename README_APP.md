# 🚗 RidePrice Pro - Real-Time Price Prediction App

A modern, real-time price prediction application for taxi companies like Uber, built with Flask, Socket.IO, and modern web technologies.

## ✨ Features

### 🎯 Core Functionality
- **Real-time Price Prediction**: Get instant price estimates for rides
- **Interactive Map**: Google Maps integration with location autocomplete
- **Dynamic Pricing**: Surge pricing based on demand/supply, weather, and traffic
- **Live Market Conditions**: Real-time updates of demand, supply, weather, and traffic
- **Price History**: Chart.js visualization of recent price predictions
- **Recent Predictions**: Track and display recent ride predictions

### 🎨 Modern UI/UX
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Real-time Updates**: Live market condition updates every 5 seconds
- **Beautiful Animations**: Smooth transitions and hover effects
- **Toast Notifications**: User-friendly success/error messages
- **Loading States**: Professional loading overlays

### 🔧 Technical Features
- **WebSocket Communication**: Real-time bidirectional communication
- **Google Maps API**: Interactive map with autocomplete
- **Chart.js Integration**: Beautiful price history charts
- **Geolocation Services**: Accurate distance calculations
- **Modular Architecture**: Clean, maintainable code structure

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Maps API Key (optional for full functionality)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ride-price-prediction
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Maps API (Optional)**
   - Get a Google Maps API key from [Google Cloud Console](https://console.cloud.google.com/)
   - Replace `YOUR_GOOGLE_MAPS_API_KEY` in `templates/index.html` with your actual API key

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - The app will be running with real-time features

## 📊 How It Works

### Price Prediction Algorithm
The application uses a sophisticated pricing model that considers:

1. **Base Fare**: $2.50 base charge
2. **Distance Rate**: $1.50 per mile
3. **Time Rate**: $0.35 per minute
4. **Surge Multiplier**: Dynamic pricing based on demand/supply
5. **Weather Multipliers**:
   - Clear: 1.0x
   - Rainy: 1.1x
   - Snowy: 1.3x
   - Stormy: 1.2x
6. **Traffic Multipliers**:
   - Normal: 1.0x
   - Heavy: 1.15x
   - Congested: 1.25x
7. **Time of Day Multipliers**:
   - Day: 1.0x
   - Rush Hour: 1.2x
   - Night: 1.1x
   - Early Morning: 1.05x

### Real-time Features
- **Market Simulation**: Simulates changing demand/supply levels
- **Weather Changes**: Random weather condition updates
- **Traffic Updates**: Dynamic traffic condition changes
- **Live Updates**: WebSocket-based real-time data transmission

## 🏗️ Architecture

### Backend (Flask + Socket.IO)
```
app.py
├── Flask Application
├── Socket.IO Server
├── Price Prediction Engine
├── Real-time Data Simulation
└── API Endpoints
```

### Frontend (HTML + CSS + JavaScript)
```
templates/
├── index.html (Main UI)
static/
├── css/
│   └── style.css (Modern styling)
└── js/
    └── app.js (Interactive features)
```

### Key Components
- **PricePredictor Class**: Core pricing algorithm
- **Real-time Simulation**: Background thread for market data
- **WebSocket Handlers**: Real-time communication
- **Google Maps Integration**: Interactive mapping
- **Chart.js**: Price history visualization

## 🎯 Usage Guide

### Making a Price Prediction
1. **Enter Pickup Location**: Type or select your pickup location
2. **Enter Dropoff Location**: Type or select your destination
3. **View Route**: The map will show the route between locations
4. **Get Prediction**: Click "Predict Price" to get instant pricing
5. **View Details**: See distance, duration, and surge multiplier
6. **Track History**: View recent predictions and price trends

### Understanding Market Conditions
- **Demand Level**: Current ride demand (0.1 - 1.0)
- **Supply Level**: Available drivers (0.1 - 1.0)
- **Weather**: Current weather conditions affecting pricing
- **Traffic**: Real-time traffic conditions
- **Surge Multiplier**: Current price multiplier

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set Flask secret key
export FLASK_SECRET_KEY="your-secret-key"

# Optional: Set Google Maps API key
export GOOGLE_MAPS_API_KEY="your-api-key"
```

### Customizing Pricing
Edit the `PricePredictor` class in `app.py` to modify:
- Base fare rates
- Distance/time multipliers
- Weather/traffic multipliers
- Surge pricing logic

## 📈 API Endpoints

### REST API
- `GET /`: Main application page
- `POST /predict`: Price prediction endpoint
- `GET /api/current-conditions`: Current market conditions

### WebSocket Events
- `connect`: Client connection
- `request_prediction`: Price prediction request
- `real_time_update`: Market condition updates
- `prediction_result`: Prediction results
- `prediction_error`: Error handling

## 🛠️ Development

### Project Structure
```
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css     # Modern CSS styles
│   └── js/
│       └── app.js        # Frontend JavaScript
├── models/               # ML models (if applicable)
└── README_APP.md         # This file
```

### Adding Features
1. **New Pricing Factors**: Modify `PricePredictor.predict_price()`
2. **Additional UI Components**: Add to `templates/index.html`
3. **Real-time Features**: Extend WebSocket handlers in `app.py`
4. **Map Features**: Enhance Google Maps integration in `static/js/app.js`

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -k gevent -w 1 --bind 0.0.0.0:5000 app:app

# Using Docker
docker build -t ride-price-app .
docker run -p 5000:5000 ride-price-app
```

### Environment Setup
- **Development**: `FLASK_ENV=development`
- **Production**: `FLASK_ENV=production`

## 🔒 Security Considerations

- **API Key Protection**: Keep Google Maps API key secure
- **Input Validation**: All user inputs are validated
- **Error Handling**: Comprehensive error handling throughout
- **Rate Limiting**: Consider implementing rate limiting for production

## 📱 Browser Compatibility

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the code comments

## 🎉 Acknowledgments

- **Flask**: Web framework
- **Socket.IO**: Real-time communication
- **Google Maps**: Mapping services
- **Chart.js**: Data visualization
- **Font Awesome**: Icons
- **Inter Font**: Typography

---

**Built with ❤️ for the ride-sharing industry**