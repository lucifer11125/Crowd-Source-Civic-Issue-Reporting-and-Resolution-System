from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath('instance/complaints.db')
db = SQLAlchemy(app)

print('DB URI:', app.config['SQLALCHEMY_DATABASE_URI'])

with app.app_context():
    db.create_all()
    print('SQLAlchemy connected successfully')
