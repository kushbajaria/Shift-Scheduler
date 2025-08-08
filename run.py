#!/usr/bin/env python3
"""
Startup script for the Shift Scheduler Flask application.
This script will initialize the database if needed and start the server.
"""

import os
import sys
import socket

# Add the project root to Python path
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

def find_available_port():
    """Find an available port"""
    preferred_ports = [8080, 8000, 3000, 8888, 9000, 8001, 8002, 8003]
    
    for port in preferred_ports:
        if not is_port_in_use(port):
            return port
    
    # If none of the preferred ports are available, find any available port
    for port in range(8080, 9000):
        if not is_port_in_use(port):
            return port
    
    return None

def check_database():
    """Check if database exists and is properly initialized"""
    # The app.py file now handles database initialization automatically
    # Just check if the instance directory exists
    instance_dir = os.path.join(project_root, 'instance')
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir, exist_ok=True)
        print("⚠️  Database directory created. Database will be initialized automatically.")
    return True

def start_application():
    """Start the Flask application"""
    try:
        # Check database first
        if not check_database():
            return
        
        # Find an available port
        port = find_available_port()
        if port is None:
            print("❌ No available ports found between 8080-9000")
            return
            
        print("🚀 Starting Shift Scheduler SPA...")
        print(f"📊 Access the application at: http://localhost:{port}")
        print("🌟 Modern Single Page Application with full backend")
        print("👤 Default admin login:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n📝 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Set the port in environment for the app
        os.environ['PORT'] = str(port)
        
        # Import and run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    start_application()
