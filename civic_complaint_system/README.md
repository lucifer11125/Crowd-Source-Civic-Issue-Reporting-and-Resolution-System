# Civic Complaint Management System

A complete Flask-based web application for managing civic complaints with role-based access control, auto-assignment, and reporting capabilities.

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python app.py
   ```

3. **Access the System**
   - Open: http://localhost:5000
   - Register your first admin account

## 📋 Features

### User Roles
- **Citizen**: Submit and track complaints
- **Municipal Officer**: Manage assigned complaints by department
- **Administrator**: Full system access, user management, and reporting

### Core Features
- ✅ User authentication with role-based access control
- ✅ Complaint submission with photo uploads (max 5MB)
- ✅ Auto-assignment to appropriate departments
- ✅ Status tracking with detailed timeline
- ✅ Admin dashboard with system statistics
- ✅ User management and role assignment
- ✅ CSV report generation with filters
- ✅ Responsive Bootstrap 5 design
- ✅ Mobile-friendly interface

## 🏗️ Project Structure

```
civic_complaint_system/
├── app.py                     # Main Flask application
├── config.py                  # Configuration management
├── models.py                  # Database models (User, Complaint, StatusUpdate)
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── routes/                    # URL route handlers
│   ├── __init__.py           # Blueprint initialization
│   ├── auth.py               # Authentication routes
│   ├── main.py               # Main application routes
│   ├── complaints.py         # Complaint management routes
│   └── admin.py              # Admin-only routes
├── templates/                 # Jinja2 HTML templates
├── static/                    # Static files
│   ├── css/style.css         # Custom styling
│   ├── js/main.js            # JavaScript functionality
│   └── uploads/              # User uploaded images
└── instance/                  # SQLite database (auto-created)
```

## 🗄️ Database Schema

### User Model
- ID, Name, Email, Password Hash, Role, Department, Status, Created At

### Complaint Model
- ID, User ID, Assigned Officer ID, Category, Description, Address,
- Landmark, Image Filename, Status, Priority, Resolution Notes,
- Created/Updated/Resolved Timestamps

### StatusUpdate Model
- ID, Complaint ID, Updated By, Old/New Status, Note, Timestamp

## 🔧 Configuration

Environment variables in `.env`:
```
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=5242880
DATABASE_URL=sqlite:///instance/complaints.db
```

## 📊 Auto-Assignment Logic

Complaints are automatically assigned based on category:
- **potholes, streetlight** → roads department
- **garbage** → sanitation department
- **water_supply, drainage** → water department
- **other** → general administration

Assignment goes to the officer with fewest active complaints in the relevant department.

## 🎨 Categories & Departments

### Complaint Categories
- Potholes & Road Damage
- Street Light Issues
- Garbage Collection
- Water Supply Issues
- Drainage Problems
- Other Issues

### Departments
- Roads & Transportation
- Water Supply & Drainage
- Sanitation & Waste Management
- General Administration
- System Administration

## 📱 Responsive Design

- Mobile-first approach with Bootstrap 5
- Collapsible navigation
- Touch-friendly forms
- Responsive tables and cards
- Optimized for all screen sizes

## 🔒 Security Features

- Password hashing with Werkzeug
- Session-based authentication with Flask-Login
- Role-based access control decorators
- Input validation and sanitization
- Secure file upload handling
- CSRF protection (Flask-WTF)
- SQL injection prevention (SQLAlchemy ORM)

## 📈 Reporting System

Admin can generate CSV reports with filters:
- Date range selection
- Status filtering
- Category filtering
- Department filtering
- Complete complaint details with status history

## 🚀 Deployment Notes

### Development
```bash
python app.py
```

### Production (Recommended)
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Setup
- Set `FLASK_ENV=production`
- Use proper database (PostgreSQL/MySQL)
- Configure `SECRET_KEY` with secure value
- Set up file storage (S3/Azure recommended)
- Enable HTTPS with SSL certificate

## 🎯 Demo Workflow

1. **Registration**: Create citizen, officer, and admin accounts
2. **Complaint Submission**: Citizens submit issues with photos
3. **Auto-Assignment**: System assigns to appropriate department
4. **Status Updates**: Officers update complaint progress
5. **Timeline Tracking**: Citizens view complete status history
6. **Admin Oversight**: Admin manages users and generates reports

## 🛠️ Customization

- Modify `config.py` for database and app settings
- Update `.env` for environment variables
- Customize templates in `templates/` directory
- Style changes in `static/css/style.css`
- Add new routes in `routes/` modules
- Extend models in `models.py`

## 📞 Support

The application includes comprehensive error handling, form validation, and user guidance throughout the interface.

---

**Built with Flask, SQLAlchemy, Bootstrap 5, and ❤️**