#!/usr/bin/env python3
"""
Demo script for the Uber-Style Real-Time Price Prediction Application
Shows key features and capabilities
"""

import requests
import json
import time
import random
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"

def demo_price_prediction():
    """Demonstrate price prediction with different scenarios"""
    print("🚗 Price Prediction Demo")
    print("=" * 40)
    
    # Sample routes around NYC
    routes = [
        {
            "name": "Times Square to Central Park",
            "pickup": (40.7589, -73.9851),
            "dropoff": (40.7829, -73.9654)
        },
        {
            "name": "Brooklyn Bridge to Manhattan",
            "pickup": (40.7061, -73.9969),
            "dropoff": (40.7589, -73.9851)
        },
        {
            "name": "JFK Airport to Manhattan",
            "pickup": (40.6413, -73.7781),
            "dropoff": (40.7589, -73.9851)
        }
    ]
    
    ride_types = ["economy", "comfort", "premium", "luxury"]
    
    for route in routes:
        print(f"\n📍 Route: {route['name']}")
        print("-" * 30)
        
        for ride_type in ride_types:
            try:
                payload = {
                    "pickup_lat": route["pickup"][0],
                    "pickup_lng": route["pickup"][1],
                    "dropoff_lat": route["dropoff"][0],
                    "dropoff_lng": route["dropoff"][1],
                    "ride_type": ride_type
                }
                
                response = requests.post(f"{BASE_URL}/predict-price", json=payload, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  {ride_type.title():8}: ${data['total_price']:6.2f} "
                          f"(Base: ${data['base_price']:.2f}, Surge: {data['surge_multiplier']:.2f}x)")
                else:
                    print(f"  {ride_type.title():8}: Error - {response.status_code}")
                    
            except Exception as e:
                print(f"  {ride_type.title():8}: Error - {e}")

def demo_market_simulation():
    """Demonstrate market simulation with changing demand/supply"""
    print("\n\n📊 Market Simulation Demo")
    print("=" * 40)
    
    scenarios = [
        {"name": "Normal Market", "demand": 1.0, "supply": 1.0},
        {"name": "High Demand", "demand": 1.8, "supply": 1.0},
        {"name": "Low Supply", "demand": 1.0, "supply": 0.6},
        {"name": "Surge Pricing", "demand": 1.5, "supply": 0.8},
        {"name": "Balanced Market", "demand": 1.0, "supply": 1.0}
    ]
    
    test_route = {
        "pickup_lat": 40.7589,
        "pickup_lng": -73.9851,
        "dropoff_lat": 40.7484,
        "dropoff_lng": -73.9857,
        "ride_type": "economy"
    }
    
    for scenario in scenarios:
        print(f"\n🎯 Scenario: {scenario['name']}")
        print("-" * 25)
        
        try:
            # Update market conditions
            requests.post(f"{BASE_URL}/api/update-demand", json=scenario["demand"], timeout=2)
            requests.post(f"{BASE_URL}/api/update-supply", json=scenario["supply"], timeout=2)
            
            # Wait for updates to take effect
            time.sleep(1)
            
            # Get market status
            status_response = requests.get(f"{BASE_URL}/api/market-status", timeout=2)
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"  Market: Demand={status['demand']:.2f}, Supply={status['supply']:.2f}")
                print(f"  Surge Multiplier: {status['surge_multiplier']:.2f}x")
            
            # Predict price
            price_response = requests.post(f"{BASE_URL}/predict-price", json=test_route, timeout=2)
            if price_response.status_code == 200:
                price_data = price_response.json()
                print(f"  Price: ${price_data['total_price']:.2f} (Base: ${price_data['base_price']:.2f})")
                print(f"  Distance: {price_data['estimated_distance']:.2f} km")
                print(f"  Duration: {price_data['estimated_duration']} min")
            
        except Exception as e:
            print(f"  Error: {e}")

def demo_real_time_updates():
    """Demonstrate real-time market updates"""
    print("\n\n⚡ Real-Time Updates Demo")
    print("=" * 40)
    print("Monitoring market changes for 30 seconds...")
    print("(Press Ctrl+C to stop early)")
    
    start_time = time.time()
    update_count = 0
    
    try:
        while time.time() - start_time < 30:
            try:
                response = requests.get(f"{BASE_URL}/api/market-status", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    update_count += 1
                    
                    # Calculate market efficiency
                    efficiency = min(data['demand'], data['supply']) / max(data['demand'], data['supply']) * 100
                    
                    print(f"\r  Update {update_count:2d}: "
                          f"Demand={data['demand']:.2f}, "
                          f"Supply={data['supply']:.2f}, "
                          f"Surge={data['surge_multiplier']:.2f}x, "
                          f"Efficiency={efficiency:.1f}%", end="")
                
                time.sleep(2)
                
            except KeyboardInterrupt:
                print("\n\n⏹️ Demo stopped by user")
                break
            except Exception as e:
                print(f"\n  Error: {e}")
                break
                
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo stopped by user")
    
    print(f"\n\n📈 Total updates: {update_count}")

def demo_api_endpoints():
    """Demonstrate all available API endpoints"""
    print("\n\n🔌 API Endpoints Demo")
    print("=" * 40)
    
    endpoints = [
        {
            "name": "Market Status",
            "method": "GET",
            "url": "/api/market-status",
            "description": "Get current market conditions"
        },
        {
            "name": "Price Prediction",
            "method": "POST",
            "url": "/predict-price",
            "description": "Predict ride price"
        },
        {
            "name": "Update Demand",
            "method": "POST",
            "url": "/api/update-demand",
            "description": "Update demand factor"
        },
        {
            "name": "Update Supply",
            "method": "POST",
            "url": "/api/update-supply",
            "description": "Update supply factor"
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n📡 {endpoint['name']}")
        print(f"   Method: {endpoint['method']}")
        print(f"   URL: {endpoint['url']}")
        print(f"   Description: {endpoint['description']}")
        
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(f"{BASE_URL}{endpoint['url']}", timeout=5)
            elif endpoint['method'] == 'POST':
                if 'demand' in endpoint['url']:
                    response = requests.post(f"{BASE_URL}{endpoint['url']}", json=1.0, timeout=5)
                elif 'supply' in endpoint['url']:
                    response = requests.post(f"{BASE_URL}{endpoint['url']}", json=1.0, timeout=5)
                else:
                    # Price prediction
                    payload = {
                        "pickup_lat": 40.7589,
                        "pickup_lng": -73.9851,
                        "dropoff_lat": 40.7484,
                        "dropoff_lng": -73.9857,
                        "ride_type": "economy"
                    }
                    response = requests.post(f"{BASE_URL}{endpoint['url']}", json=payload, timeout=5)
            
            if response.status_code == 200:
                print(f"   Status: ✅ Working (200)")
                if endpoint['name'] == 'Market Status':
                    data = response.json()
                    print(f"   Response: Demand={data['demand']:.2f}, Supply={data['supply']:.2f}")
                elif endpoint['name'] == 'Price Prediction':
                    data = response.json()
                    print(f"   Response: ${data['total_price']:.2f}")
            else:
                print(f"   Status: ❌ Error ({response.status_code})")
                
        except Exception as e:
            print(f"   Status: ❌ Error ({e})")

def main():
    """Main demo function"""
    print("🎬 Uber-Style Real-Time Price Prediction - Demo")
    print("=" * 60)
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/market-status", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding properly")
            return
    except:
        print("❌ Server is not running. Please start the application first:")
        print("   python app.py")
        return
    
    print("✅ Server is running and responding")
    
    # Run demos
    try:
        demo_price_prediction()
        demo_market_simulation()
        demo_api_endpoints()
        
        # Ask user if they want to see real-time updates
        print("\n" + "=" * 60)
        choice = input("Would you like to see real-time market updates? (y/n): ").strip().lower()
        
        if choice in ['y', 'yes']:
            demo_real_time_updates()
        
        print("\n🎉 Demo completed!")
        print("\n📋 Next steps:")
        print("• Open http://localhost:8000 for the web interface")
        print("• Open http://localhost:8501 for the analytics dashboard")
        print("• Run 'python test_app.py' for comprehensive testing")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")

if __name__ == "__main__":
    main()