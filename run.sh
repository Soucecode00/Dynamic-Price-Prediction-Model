#!/bin/bash

# TaxiPrice AI Startup Script
# This script sets up and runs the complete application

echo "🚀 Starting TaxiPrice AI Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.9 or later."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 16 or later."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install

# Initialize ML model
if [ ! -f "models/price_model.pkl" ]; then
    print_status "Training initial ML model..."
    python price_model.py
    print_success "ML model trained and saved"
else
    print_status "ML model already exists, skipping training"
fi

# Create logs directory
mkdir -p logs

# Function to start backend
start_backend() {
    print_status "Starting Flask backend server..."
    python app.py &
    BACKEND_PID=$!
    echo $BACKEND_PID > backend.pid
    
    # Wait for backend to start
    sleep 5
    
    # Check if backend is running
    if curl -s http://localhost:5000/api/market_data > /dev/null; then
        print_success "Backend server is running on http://localhost:5000"
    else
        print_error "Failed to start backend server"
        return 1
    fi
}

# Function to start frontend
start_frontend() {
    print_status "Starting React frontend server..."
    npm start &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > frontend.pid
    
    print_success "Frontend server is starting on http://localhost:3000"
    print_status "Please wait for the frontend to compile..."
}

# Function to stop servers
stop_servers() {
    print_status "Stopping servers..."
    
    if [ -f backend.pid ]; then
        BACKEND_PID=$(cat backend.pid)
        kill $BACKEND_PID 2>/dev/null
        rm backend.pid
        print_success "Backend server stopped"
    fi
    
    if [ -f frontend.pid ]; then
        FRONTEND_PID=$(cat frontend.pid)
        kill $FRONTEND_PID 2>/dev/null
        rm frontend.pid
        print_success "Frontend server stopped"
    fi
    
    # Kill any remaining processes
    pkill -f "python app.py" 2>/dev/null
    pkill -f "npm start" 2>/dev/null
    pkill -f "react-scripts start" 2>/dev/null
}

# Handle script termination
trap stop_servers EXIT INT TERM

# Check command line arguments
case "${1:-start}" in
    "start")
        print_status "Starting TaxiPrice AI in development mode..."
        start_backend
        if [ $? -eq 0 ]; then
            start_frontend
            
            echo ""
            print_success "🎉 TaxiPrice AI is now running!"
            echo ""
            echo -e "${BLUE}📊 Dashboard:${NC}     http://localhost:3000"
            echo -e "${BLUE}🧮 Calculator:${NC}    http://localhost:3000/calculator"
            echo -e "${BLUE}📈 Analytics:${NC}     http://localhost:3000/analytics"
            echo -e "${BLUE}🔧 API:${NC}           http://localhost:5000"
            echo ""
            print_status "Press Ctrl+C to stop all servers"
            
            # Wait for user interrupt
            wait
        else
            print_error "Failed to start application"
            exit 1
        fi
        ;;
    
    "stop")
        stop_servers
        ;;
    
    "restart")
        stop_servers
        sleep 2
        start_backend && start_frontend
        ;;
    
    "backend")
        start_backend
        wait
        ;;
    
    "frontend")
        start_frontend
        wait
        ;;
    
    "docker")
        print_status "Starting TaxiPrice AI with Docker..."
        if ! command -v docker-compose &> /dev/null; then
            print_error "Docker Compose is not installed"
            exit 1
        fi
        docker-compose up -d
        print_success "TaxiPrice AI is running in Docker containers"
        echo ""
        echo -e "${BLUE}📊 Application:${NC}   http://localhost:3000"
        echo -e "${BLUE}🔧 API:${NC}           http://localhost:5000"
        echo ""
        print_status "Use 'docker-compose down' to stop"
        ;;
    
    "test")
        print_status "Running tests..."
        
        # Backend tests
        print_status "Running backend tests..."
        python -m pytest tests/ -v
        
        # Frontend tests
        print_status "Running frontend tests..."
        npm test -- --watchAll=false --coverage
        
        print_success "All tests completed"
        ;;
    
    "build")
        print_status "Building production application..."
        
        # Build frontend
        npm run build
        print_success "Frontend built successfully"
        
        # Create production package
        print_status "Creating production package..."
        tar -czf taxiprice-ai-production.tar.gz \
            build/ \
            *.py \
            requirements.txt \
            models/ \
            README.md \
            docker-compose.yml \
            Dockerfile.*
        
        print_success "Production package created: taxiprice-ai-production.tar.gz"
        ;;
    
    "help"|"--help"|"-h")
        echo "TaxiPrice AI Startup Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  start     Start both backend and frontend (default)"
        echo "  stop      Stop all running servers"
        echo "  restart   Restart all servers"
        echo "  backend   Start only the backend server"
        echo "  frontend  Start only the frontend server"
        echo "  docker    Start with Docker Compose"
        echo "  test      Run all tests"
        echo "  build     Build production package"
        echo "  help      Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run.sh              # Start in development mode"
        echo "  ./run.sh docker       # Start with Docker"
        echo "  ./run.sh test         # Run tests"
        echo ""
        ;;
    
    *)
        print_error "Unknown command: $1"
        echo "Use './run.sh help' for usage information"
        exit 1
        ;;
esac