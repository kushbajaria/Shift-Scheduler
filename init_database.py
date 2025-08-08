#!/usr/bin/env python3
"""
Database initialization script for the Shift Scheduler application.
Run this script first to create the database and admin user.
"""

import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from flask import Flask
from workscheduler.classes import User, Schedule, db

def init_database():
    """Initialize the database and create admin user"""
    
    # Create Flask app with proper configuration
    app = Flask(__name__, 
               template_folder='workscheduler/templates',
               static_folder='workscheduler/static')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scheduler.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'your_secure_random_secret_key'
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully!")
            
            # Create admin user if it doesn't exist
            if not User.query.filter_by(username='admin').first():
                admin_user = User(
                    username='admin',
                    first_name='Admin',
                    last_name='User',
                    email='admin@example.com',
                    phone='555-1234',
                    address='123 Admin St',
                    sick_hours=0,
                    pto_hours=0,
                    hourly_rate=0,
                    job_assignment='Administrator',
                    hire_date='2020-01-15',
                    role='admin'
                )
                admin_user.set_password('admin123')  # Default admin password
                db.session.add(admin_user)
                db.session.commit()
                print("✓ Admin user created successfully!")
                print("  Username: admin")
                print("  Password: admin123")
            else:
                print("✓ Admin user already exists.")
                
            print("\n🎉 Database initialization completed!")
            print("You can now run the application with: python app.py")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    init_database()
