#!/usr/bin/env python3
"""Quick test to check for common issues"""

import os
import sys
import socket

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """Test all required imports"""
    try:
        print("Testing imports...")
        
        # Test Flask
        from flask import Flask
        print("✓ Flask imported")
        
        # Test workscheduler modules
        from workscheduler.classes import User, Schedule, db
        print("✓ Classes imported")
        
        from workscheduler.core import login_required, admin_required, generate_shifts, get_week_dates, datetimeformat
        print("✓ Core modules imported")
        
        # Test config
        from config import DevelopmentConfig, ProductionConfig
        print("✓ Config imported")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ports():
    """Test available ports"""
    print("\nTesting ports...")
    
    def is_port_available(port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    test_ports = [5000, 8000, 8080, 3000, 8888, 9000]
    available_ports = []
    
    for port in test_ports:
        if is_port_available(port):
            available_ports.append(port)
            print(f"✓ Port {port} is available")
        else:
            print(f"❌ Port {port} is in use")
    
    if available_ports:
        print(f"\n🎉 Available ports: {available_ports}")
        return available_ports[0]
    else:
        print("❌ No common ports available")
        return None

def test_database():
    """Test database setup"""
    try:
        print("\nTesting database...")
        
        # Set test environment
        os.environ['FLASK_ENV'] = 'testing'
        
        from app import app
        from workscheduler.classes import db, User
        
        with app.app_context():
            # Test database creation
            db.create_all()
            print("✓ Database tables created")
            
            # Test admin user
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("✓ Admin user exists")
            else:
                print("⚠️  Admin user not found (will be created on startup)")
            
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 Diagnosing Shift Scheduler issues...\n")
    
    # Test imports
    if not test_imports():
        print("\n❌ Import issues found. Please install dependencies:")
        print("   pip install -r requirements.txt")
        return
    
    # Test ports
    available_port = test_ports()
    if not available_port:
        print("\n❌ No available ports. Try:")
        print("   sudo lsof -ti:5000,8000,8080 | xargs kill -9")
        return
    
    # Test database
    if not test_database():
        print("\n❌ Database issues found. Try:")
        print("   python init_database.py")
        return
    
    print(f"\n🎉 All tests passed!")
    print(f"✅ Ready to run on port {available_port}")
    print("\n🚀 To start the app, run:")
    print("   python run.py")
    print("   python app.py")
    print("   python start_app.py")

if __name__ == '__main__':
    main()
