import sys
import os
sys.path.append('civic_complaint_system')
os.chdir('civic_complaint_system')

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Complaint, StatusUpdate, get_auto_assignment_department, find_best_officer_for_assignment
from config import config
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.config.from_object(config['development'])

db.init_app(app)

def add_30_complaints():
    with app.app_context():
        # Get the citizen user
        citizen = User.query.filter_by(email='citizen@smart.com').first()
        if not citizen:
            print("Citizen user not found. Please run restore_original_data.py first.")
            return

        # Sample addresses in Indian cities
        addresses = [
            "MG Road, Bangalore", "Connaught Place, Delhi", "Marine Drive, Mumbai",
            "Anna Salai, Chennai", "Sector 17, Chandigarh", "Banjara Hills, Hyderabad",
            "Salt Lake City, Kolkata", "Rajouri Garden, Delhi", "Koramangala, Bangalore",
            "Andheri West, Mumbai", "T. Nagar, Chennai", "Punjabi Bagh, Delhi",
            "Gachibowli, Hyderabad", "Salt Lake, Kolkata", "Jayanagar, Bangalore",
            "Bandra East, Mumbai", "Adyar, Chennai", "Karol Bagh, Delhi",
            "Jubilee Hills, Hyderabad", "New Town, Kolkata", "Whitefield, Bangalore",
            "Powai, Mumbai", "Velachery, Chennai", "Dwarka, Delhi",
            "Hitech City, Hyderabad", "Park Street, Kolkata", "Indiranagar, Bangalore",
            "Lower Parel, Mumbai", "Nungambakkam, Chennai", "Lajpat Nagar, Delhi"
        ]

        # Complaint data from user feedback
        complaints_data = [
            {'id': 1, 'category': 'potholes', 'department': 'roads', 'priority': 'high', 'status': 'in_progress', 'description': 'Large pothole causing traffic near main road'},
            {'id': 2, 'category': 'potholes', 'department': 'roads', 'priority': 'medium', 'status': 'resolved', 'description': 'Cracked pavement repaired near school'},
            {'id': 3, 'category': 'potholes', 'department': 'roads', 'priority': 'low', 'status': 'submitted', 'description': 'Uneven speed breaker damaging vehicles'},
            {'id': 4, 'category': 'potholes', 'department': 'roads', 'priority': 'high', 'status': 'rejected', 'description': 'Request for road widening not approved'},
            {'id': 5, 'category': 'streetlight', 'department': 'roads', 'priority': 'high', 'status': 'in_progress', 'description': 'Entire street dark due to multiple lights off'},
            {'id': 6, 'category': 'streetlight', 'department': 'roads', 'priority': 'medium', 'status': 'resolved', 'description': 'Faulty streetlight replaced near bus stop'},
            {'id': 7, 'category': 'streetlight', 'department': 'roads', 'priority': 'low', 'status': 'submitted', 'description': 'Dim light outside community park'},
            {'id': 8, 'category': 'streetlight', 'department': 'roads', 'priority': 'medium', 'status': 'rejected', 'description': 'Complaint about private society light ignored'},
            {'id': 9, 'category': 'garbage', 'department': 'sanitation', 'priority': 'high', 'status': 'in_progress', 'description': 'Overflowing bins attracting stray dogs'},
            {'id': 10, 'category': 'garbage', 'department': 'sanitation', 'priority': 'high', 'status': 'resolved', 'description': 'Garbage cleared near market area'},
            {'id': 11, 'category': 'garbage', 'department': 'sanitation', 'priority': 'medium', 'status': 'submitted', 'description': 'Garbage truck skips scheduled visit'},
            {'id': 12, 'category': 'garbage', 'department': 'sanitation', 'priority': 'low', 'status': 'rejected', 'description': 'Duplicate complaint of garbage delay'},
            {'id': 13, 'category': 'water_supply', 'department': 'water', 'priority': 'high', 'status': 'in_progress', 'description': 'No water supply since two days'},
            {'id': 14, 'category': 'water_supply', 'department': 'water', 'priority': 'medium', 'status': 'resolved', 'description': 'Leakage from public tap fixed'},
            {'id': 15, 'category': 'water_supply', 'department': 'water', 'priority': 'low', 'status': 'submitted', 'description': 'Rusty water reported from old pipes'},
            {'id': 16, 'category': 'water_supply', 'department': 'water', 'priority': 'high', 'status': 'rejected', 'description': 'Illegal connection request denied'},
            {'id': 17, 'category': 'drainage', 'department': 'water', 'priority': 'high', 'status': 'in_progress', 'description': 'Blocked drain causing road overflow'},
            {'id': 18, 'category': 'drainage', 'department': 'water', 'priority': 'medium', 'status': 'resolved', 'description': 'Open manhole near junction covered'},
            {'id': 19, 'category': 'drainage', 'department': 'water', 'priority': 'low', 'status': 'submitted', 'description': 'Poorly maintained drain behind park'},
            {'id': 20, 'category': 'drainage', 'department': 'water', 'priority': 'medium', 'status': 'rejected', 'description': 'Complaint about private drain ignored'},
            {'id': 21, 'category': 'other', 'department': 'general', 'priority': 'high', 'status': 'in_progress', 'description': 'Illegal parking blocking street entrance'},
            {'id': 22, 'category': 'other', 'department': 'general', 'priority': 'medium', 'status': 'resolved', 'description': 'Stray dogs captured near playground'},
            {'id': 23, 'category': 'other', 'department': 'general', 'priority': 'low', 'status': 'submitted', 'description': 'Broken bench in community park'},
            {'id': 24, 'category': 'other', 'department': 'general', 'priority': 'high', 'status': 'rejected', 'description': 'Construction noise within legal hours'},
            {'id': 25, 'category': 'potholes', 'department': 'roads', 'priority': 'medium', 'status': 'resolved', 'description': 'Damaged divider fixed on main road'},
            {'id': 26, 'category': 'streetlight', 'department': 'roads', 'priority': 'low', 'status': 'in_progress', 'description': 'Light remains on during daytime'},
            {'id': 27, 'category': 'garbage', 'department': 'sanitation', 'priority': 'medium', 'status': 'resolved', 'description': 'Street sweeping done after complaint'},
            {'id': 28, 'category': 'water_supply', 'department': 'water', 'priority': 'high', 'status': 'in_progress', 'description': 'Sudden water pressure drop in building'},
            {'id': 29, 'category': 'drainage', 'department': 'water', 'priority': 'medium', 'status': 'resolved', 'description': 'Clogged storm drain cleaned near market'},
            {'id': 30, 'category': 'other', 'department': 'general', 'priority': 'low', 'status': 'submitted', 'description': 'Unauthorized street banner reported'}
        ]

        for data in complaints_data:
            # Assign department and officer
            department = get_auto_assignment_department(data['category'])
            officer = find_best_officer_for_assignment(department)

            # Create complaint
            complaint = Complaint(
                user_id=citizen.id,
                assigned_department=department,
                assigned_officer=officer.id if officer else None,
                category=data['category'],
                description=data['description'],
                address=random.choice(addresses),  # Random address
                status=data['status'],
                priority=data['priority'],
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))  # Random past date
            )
            db.session.add(complaint)
            db.session.flush()  # To get complaint.id

            # Add status update if not submitted
            if data['status'] != 'submitted':
                update = StatusUpdate(
                    complaint_id=complaint.id,
                    updated_by=officer.id if officer else citizen.id,
                    old_status='submitted',
                    new_status=data['status'],
                    note=f"Status updated: {data['description']}"
                )
                db.session.add(update)

                # Update timestamps
                complaint.updated_at = datetime.utcnow()
                if data['status'] == 'resolved':
                    complaint.resolved_at = datetime.utcnow()

        db.session.commit()
        print("30 sample complaints added successfully!")

if __name__ == '__main__':
    add_30_complaints()
