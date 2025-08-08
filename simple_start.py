#!/usr/bin/env python3
"""Simple app starter that avoids complex imports during startup"""

import os
import sys
import socket

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def find_available_port():
    """Find an available port"""
    ports_to_try = [8000, 3000, 8888, 9000, 8001, 8002, 8003, 8004, 8005]
    
    for port in ports_to_try:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    return None

def main():
    """Start the application"""
    try:
        print("🚀 Starting Shift Scheduler...")
        
        # Find available port
        port = find_available_port()
        if not port:
            print("❌ No available ports found")
            print("Try: sudo lsof -ti:8000,3000,8888 | xargs kill -9")
            return
        
        print(f"📊 Starting on port {port}")
        print(f"🌐 Access at: http://localhost:{port}")
        print("👤 Login: admin / admin123")
        print("📝 Press Ctrl+C to stop")
        print("-" * 40)
        
        # Set environment
        os.environ['PORT'] = str(port)
        os.environ['FLASK_ENV'] = 'development'
        
        # Import and run Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=port)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the Shift-Scheduler directory")
        print("2. Check virtual environment is activated")
        print("3. Run: pip install -r requirements.txt")
        print("4. Try: python init_database.py")

if __name__ == '__main__':
    main()
