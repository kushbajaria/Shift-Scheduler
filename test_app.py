#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
    from workscheduler.classes import User
    
    print("✓ All imports successful")
    
    # Test app creation
    with app.app_context():
        print("✓ App context created successfully")
        
        # Create tables
        db.create_all()
        print("✓ Database tables created")
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
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
            admin_user.set_password('password123')
            db.session.add(admin_user)
            db.session.commit()
            print("✓ Admin user created")
        else:
            print("✓ Admin user already exists")
            
    print("\n🎉 App is ready! You can now run: python app.py")
    print("Default admin login: username='admin', password='password123'")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
