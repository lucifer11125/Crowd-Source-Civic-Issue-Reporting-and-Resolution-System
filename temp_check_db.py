import sqlite3
import os

db_path = 'civic_complaint_system/instance/complaints.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('Tables in database:', tables)

    # Check users table
    cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = cursor.fetchone()[0]
    print(f'Users in database: {user_count}')

    if user_count > 0:
        cursor.execute("SELECT email, name, role FROM users;")
        users = cursor.fetchall()
        print('Users:')
        for user in users:
            print(f'  - {user[0]} ({user[1]}, {user[2]})')

    # Check complaints table
    cursor.execute("SELECT COUNT(*) FROM complaints;")
    complaint_count = cursor.fetchone()[0]
    print(f'Complaints in database: {complaint_count}')

    if complaint_count > 0:
        cursor.execute("SELECT id, category, status, priority, assigned_department FROM complaints ORDER BY id DESC LIMIT 10;")
        complaints = cursor.fetchall()
        print('Last 10 Complaints:')
        for complaint in complaints:
            print(f'  - ID {complaint[0]}: {complaint[1]} ({complaint[2]}, {complaint[3]}) - {complaint[4]}')

    conn.close()
else:
    print("Database file does not exist")
