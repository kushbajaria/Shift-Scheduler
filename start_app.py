#!/usr/bin/env python3
"""Script to start the Flask app with port checking and automatic port selection"""

import socket
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except OSError:
            return True

def find_available_port(start_port=8080, max_port=9000):
    """Find an available port starting from start_port"""
    for port in range(start_port, max_port):
        if not is_port_in_use(port):
            return port
    return None

def start_app():
    """Start the Flask application"""
    try:
        # Check common ports and find available one
        preferred_ports = [8080, 8000, 3000, 8888, 9000]
        port = None
        
        for p in preferred_ports:
            if not is_port_in_use(p):
                port = p
                break
        
        if port is None:
            port = find_available_port()
            
        if port is None:
            print("❌ No available ports found between 8080-9000")
            return False
        
        print(f"🚀 Starting Shift Scheduler on port {port}...")
        print(f"📊 Access the application at: http://localhost:{port}")
        print("👤 Default admin login:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n📝 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Set the port in environment
        os.environ['PORT'] = str(port)
        
        # Import and run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=port)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    start_app()
