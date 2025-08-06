#!/usr/bin/env python3
"""
Startup script for the Uber-Style Real-Time Price Prediction Application
Launches both the main FastAPI application and the Streamlit dashboard
"""

import subprocess
import sys
import time
import threading
import os
import signal
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import fastapi
        import streamlit
        import uvicorn
        import pandas
        import numpy
        import sklearn
        import plotly
        import requests
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def start_fastapi_app():
    """Start the FastAPI application"""
    try:
        print("🚀 Starting FastAPI application...")
        subprocess.run([sys.executable, "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start FastAPI app: {e}")
    except KeyboardInterrupt:
        print("\n🛑 FastAPI application stopped")

def start_streamlit_dashboard():
    """Start the Streamlit dashboard"""
    try:
        print("📊 Starting Streamlit dashboard...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py", "--server.port", "8501"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Streamlit dashboard: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Streamlit dashboard stopped")

def main():
    """Main startup function"""
    print("🚗 Uber-Style Real-Time Price Prediction Application")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ app.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("\n📋 Application Components:")
    print("• Main Web Interface: http://localhost:8000")
    print("• Analytics Dashboard: http://localhost:8501")
    print("• API Documentation: http://localhost:8000/docs")
    
    print("\n🎯 Choose an option:")
    print("1. Start main application only (FastAPI)")
    print("2. Start dashboard only (Streamlit)")
    print("3. Start both applications")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                print("\n🚀 Starting main application...")
                start_fastapi_app()
                break
            elif choice == "2":
                print("\n📊 Starting dashboard...")
                start_streamlit_dashboard()
                break
            elif choice == "3":
                print("\n🚀 Starting both applications...")
                
                # Start FastAPI in a separate thread
                fastapi_thread = threading.Thread(target=start_fastapi_app, daemon=True)
                fastapi_thread.start()
                
                # Wait a moment for FastAPI to start
                time.sleep(3)
                
                # Start Streamlit in main thread
                start_streamlit_dashboard()
                break
            elif choice == "4":
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\n👋 Application stopped by user")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()