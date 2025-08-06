#!/usr/bin/env python3
"""
Test script for the Uber-Style Real-Time Price Prediction Application
Tests all major functionality and API endpoints
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_COORDINATES = {
    "pickup_lat": 40.7589,
    "pickup_lng": -73.9851,
    "dropoff_lat": 40.7484,
    "dropoff_lng": -73.9857
}

def test_api_connection():
    """Test basic API connectivity"""
    print("🔍 Testing API connection...")
    try:
        response = requests.get(f"{BASE_URL}/api/market-status", timeout=5)
        if response.status_code == 200:
            print("✅ API connection successful")
            return True
        else:
            print(f"❌ API connection failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_price_prediction():
    """Test price prediction endpoint"""
    print("\n💰 Testing price prediction...")
    
    test_cases = [
        {"ride_type": "economy", "name": "Economy Ride"},
        {"ride_type": "comfort", "name": "Comfort Ride"},
        {"ride_type": "premium", "name": "Premium Ride"},
        {"ride_type": "luxury", "name": "Luxury Ride"}
    ]
    
    for test_case in test_cases:
        try:
            payload = {**TEST_COORDINATES, "ride_type": test_case["ride_type"]}
            response = requests.post(f"{BASE_URL}/predict-price", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {test_case['name']}: ${data['total_price']:.2f} (Surge: {data['surge_multiplier']:.2f}x)")
                
                # Validate response structure
                required_fields = ['base_price', 'total_price', 'surge_multiplier', 'estimated_distance', 'estimated_duration']
                for field in required_fields:
                    if field not in data:
                        print(f"❌ Missing field in response: {field}")
                        return False
            else:
                print(f"❌ {test_case['name']} failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {test_case['name']} failed: {e}")
            return False
    
    return True

def test_market_status():
    """Test market status endpoint"""
    print("\n📊 Testing market status...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/market-status", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Market Status: Demand={data['demand']:.2f}, Supply={data['supply']:.2f}, Surge={data['surge_multiplier']:.2f}x")
            
            # Validate response structure
            required_fields = ['demand', 'supply', 'surge_multiplier', 'timestamp']
            for field in required_fields:
                if field not in data:
                    print(f"❌ Missing field in market status: {field}")
                    return False
            return True
        else:
            print(f"❌ Market status failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Market status failed: {e}")
        return False

def test_demand_supply_updates():
    """Test demand and supply update endpoints"""
    print("\n🎮 Testing demand/supply updates...")
    
    test_values = [
        {"demand": 1.5, "supply": 1.0},
        {"demand": 0.8, "supply": 1.2},
        {"demand": 1.0, "supply": 1.0}
    ]
    
    for test_value in test_values:
        try:
            # Test demand update
            response = requests.post(f"{BASE_URL}/api/update-demand", json=test_value["demand"], timeout=5)
            if response.status_code != 200:
                print(f"❌ Demand update failed: {response.status_code}")
                return False
            
            # Test supply update
            response = requests.post(f"{BASE_URL}/api/update-supply", json=test_value["supply"], timeout=5)
            if response.status_code != 200:
                print(f"❌ Supply update failed: {response.status_code}")
                return False
            
            print(f"✅ Updated: Demand={test_value['demand']}, Supply={test_value['supply']}")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Update failed: {e}")
            return False
    
    return True

def test_web_interface():
    """Test web interface accessibility"""
    print("\n🌐 Testing web interface...")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        
        if response.status_code == 200:
            if "Real-Time Price Prediction" in response.text:
                print("✅ Web interface accessible and contains expected content")
                return True
            else:
                print("❌ Web interface content not as expected")
                return False
        else:
            print(f"❌ Web interface failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Web interface failed: {e}")
        return False

def test_invalid_requests():
    """Test error handling for invalid requests"""
    print("\n🚫 Testing error handling...")
    
    # Test invalid coordinates
    invalid_payload = {
        "pickup_lat": 999.0,  # Invalid latitude
        "pickup_lng": -73.9851,
        "dropoff_lat": 40.7484,
        "dropoff_lng": -73.9857
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict-price", json=invalid_payload, timeout=10)
        
        # Should handle gracefully (either return error or valid response)
        if response.status_code in [200, 400, 422]:
            print("✅ Invalid request handled appropriately")
            return True
        else:
            print(f"❌ Unexpected response for invalid request: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def run_performance_test():
    """Run a simple performance test"""
    print("\n⚡ Running performance test...")
    
    start_time = time.time()
    successful_requests = 0
    total_requests = 10
    
    for i in range(total_requests):
        try:
            response = requests.post(f"{BASE_URL}/predict-price", json=TEST_COORDINATES, timeout=5)
            if response.status_code == 200:
                successful_requests += 1
        except:
            pass
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / total_requests
    
    print(f"✅ Performance: {successful_requests}/{total_requests} successful requests")
    print(f"   Average response time: {avg_time:.3f}s")
    print(f"   Total time: {total_time:.3f}s")
    
    return successful_requests == total_requests

def main():
    """Main test function"""
    print("🧪 Uber-Style Price Prediction Application - Test Suite")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    if not test_api_connection():
        print("\n❌ Server is not running. Please start the application first:")
        print("   python app.py")
        sys.exit(1)
    
    # Run all tests
    tests = [
        ("Price Prediction", test_price_prediction),
        ("Market Status", test_market_status),
        ("Demand/Supply Updates", test_demand_supply_updates),
        ("Web Interface", test_web_interface),
        ("Error Handling", test_invalid_requests),
        ("Performance", run_performance_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the application.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)