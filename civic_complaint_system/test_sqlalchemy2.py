from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/complaints.db'
db = SQLAlchemy(app)

print('Working dir:', os.getcwd())
print('DB path:', os.path.abspath('instance/complaints.db'))

# Ensure instance directory exists
os.makedirs('instance', exist_ok=True)

with app.app_context():
    db.create_all()
    print('SQLAlchemy connected successfully')
