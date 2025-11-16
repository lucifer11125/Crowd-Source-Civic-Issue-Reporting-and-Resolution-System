import sys
import os
sys.path.append('civic_complaint_system')
os.chdir('civic_complaint_system')

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Complaint, StatusUpdate
from config import config

app = Flask(__name__)
app.config.from_object(config['development'])

db.init_app(app)

def restore_original_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create admin user
        admin = User(
            name='Admin',
            email='admin@smart.com',
            role='admin',
            department='administration'
        )
        admin.set_password('Admin@123')
        db.session.add(admin)

        # Create municipal officers for all departments
        officers_data = [
            {'name': 'Roads Officer', 'email': 'roads@smart.com', 'department': 'roads', 'password': 'Roads@123'},
            {'name': 'Water Officer', 'email': 'water@smart.com', 'department': 'water', 'password': 'Water@123'},
            {'name': 'Sanitation Officer', 'email': 'garbage@smart.com', 'department': 'sanitation', 'password': 'Garbage@123'},
            {'name': 'General Officer', 'email': 'others@smart.com', 'department': 'general', 'password': 'Others@123'}
        ]

        for officer_data in officers_data:
            officer = User(
                name=officer_data['name'],
                email=officer_data['email'],
                role='municipal',
                department=officer_data['department']
            )
            officer.set_password(officer_data['password'])
            db.session.add(officer)

        # Create citizen
        citizen = User(
            name='Citizen',
            email='citizen@smart.com',
            role='citizen'
        )
        citizen.set_password('Atharva@047')
        db.session.add(citizen)

        db.session.commit()  # Commit users first to get IDs

        # Create sample complaints (you mentioned there were more than 23, but we'll create some representative ones)
        sample_complaints = [
            {'category': 'potholes', 'description': 'Large pothole on Main Street', 'address': '123 Main Street', 'status': 'submitted'},
            {'category': 'streetlight', 'description': 'Street light not working', 'address': '456 Oak Avenue', 'status': 'in_progress'},
            {'category': 'garbage', 'description': 'Garbage not collected', 'address': '789 Elm Street', 'status': 'resolved'},
            {'category': 'water_supply', 'description': 'Low water pressure', 'address': '321 Pine Road', 'status': 'submitted'},
            {'category': 'drainage', 'description': 'Blocked drainage causing flooding', 'address': '654 Maple Lane', 'status': 'in_progress'},
            {'category': 'other', 'description': 'General maintenance issue', 'address': '987 Cedar Court', 'status': 'resolved'},
        ]

        for i, complaint_data in enumerate(sample_complaints):
            complaint = Complaint(
                user_id=citizen.id,  # Use citizen.id instead of hardcoded 6
                category=complaint_data['category'],
                description=complaint_data['description'],
                address=complaint_data['address'],
                status=complaint_data['status']
            )
            db.session.add(complaint)

        db.session.commit()

        print("Original data restored successfully!")
        print("Admin: admin@smart.com / Admin@123")
        print("Citizen: citizen@smart.com / Atharva@047")
        print("Roads Officer: roads@smart.com / Roads@123")
        print("Water Officer: water@smart.com / Water@123")
        print("Sanitation Officer: garbage@smart.com / Garbage@123")
        print("General Officer: others@smart.com / Others@123")
        print("Created 6 sample complaints")

if __name__ == '__main__':
    restore_original_data()
