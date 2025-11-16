from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Complaint, StatusUpdate
from config import config
import os

app = Flask(__name__)
app.config.from_object(config['development'])

db.init_app(app)

def create_sample_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create admin user
        admin = User(
            name='Admin User',
            email='admin@example.com',
            role='admin',
            department='administration'
        )
        admin.set_password('Admin123!')
        db.session.add(admin)

        # Create municipal officers for all departments
        officers_data = [
            {'name': 'John Officer', 'email': 'officer@example.com', 'department': 'roads'},
            {'name': 'Mary Sanitation', 'email': 'sanitation@example.com', 'department': 'sanitation'},
            {'name': 'Bob Water', 'email': 'water@example.com', 'department': 'water'},
            {'name': 'Alice General', 'email': 'general@example.com', 'department': 'general'}
        ]

        for officer_data in officers_data:
            officer = User(
                name=officer_data['name'],
                email=officer_data['email'],
                role='municipal',
                department=officer_data['department']
            )
            officer.set_password('Officer123!')
            db.session.add(officer)

        # Create citizen
        citizen = User(
            name='Jane Citizen',
            email='citizen@example.com',
            role='citizen'
        )
        citizen.set_password('Citizen123!')
        db.session.add(citizen)

        # Create sample complaints
        complaint1 = Complaint(
            user_id=3,  # citizen
            category='potholes',
            description='Large pothole on Main Street causing traffic issues',
            address='123 Main Street',
            landmark='Near Central Park',
            status='pending'
        )
        db.session.add(complaint1)

        complaint2 = Complaint(
            user_id=3,  # citizen
            category='streetlight',
            description='Street light not working for 3 days',
            address='456 Oak Avenue',
            landmark='Corner of Oak and Pine',
            status='in_progress'
        )
        db.session.add(complaint2)

        complaint3 = Complaint(
            user_id=3,  # citizen
            category='garbage',
            description='Garbage not collected for a week',
            address='789 Elm Street',
            landmark='Near City Hall',
            status='resolved'
        )
        db.session.add(complaint3)

        db.session.commit()

        # Create status updates
        update1 = StatusUpdate(
            complaint_id=2,
            updated_by=2,  # officer
            old_status='pending',
            new_status='in_progress',
            note='Assigned to maintenance team'
        )
        db.session.add(update1)

        update2 = StatusUpdate(
            complaint_id=3,
            updated_by=2,  # officer
            old_status='in_progress',
            new_status='resolved',
            note='Issue resolved - garbage collected'
        )
        db.session.add(update2)

        db.session.commit()

        print("Sample data created successfully!")
        print("Admin: admin@example.com / Admin123!")
        print("Officer: officer@example.com / Officer123!")
        print("Citizen: citizen@example.com / Citizen123!")

if __name__ == '__main__':
    create_sample_data()
