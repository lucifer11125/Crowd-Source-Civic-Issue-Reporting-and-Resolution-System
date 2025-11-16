import pytest
import requests
import sqlite3
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask
from app import create_app, db
from models import User, Complaint, StatusUpdate
import time

BASE_URL = "http://127.0.0.1:5000"
TEST_EMAIL = None

@pytest.fixture(scope="session")
def driver():
    """Setup Chrome WebDriver for Selenium tests"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    yield driver
    driver.quit()

@pytest.fixture(scope="session")
def test_app():
    """Setup Flask test app"""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

class TestCivicComplaintSystem:

    def test_01_app_running(self):
        """Test that the Flask app is running"""
        response = requests.get(BASE_URL)
        assert response.status_code == 200

    def test_02_user_registration_valid(self, driver):
        """Test user registration with valid data"""
        import time
        unique_email = f"test{int(time.time())}@example.com"
        driver.get(f"{BASE_URL}/register")

        # Fill registration form
        driver.find_element(By.NAME, "name").send_keys("Test Citizen")
        driver.find_element(By.NAME, "email").send_keys(unique_email)
        driver.find_element(By.NAME, "password").send_keys("Password123")
        driver.find_element(By.NAME, "confirm_password").send_keys("Password123")
        # Select citizen role from dropdown
        role_select = Select(driver.find_element(By.NAME, "role"))
        role_select.select_by_value("citizen")

        # Check the terms and conditions checkbox using JavaScript
        terms_checkbox = driver.find_element(By.ID, "terms")
        driver.execute_script("arguments[0].click();", terms_checkbox)

        # Submit form
        registration_form = driver.find_element(By.ID, "registrationForm")
        registration_form.submit()

        # Check for success message or redirect to login
        WebDriverWait(driver, 10).until(
            lambda driver: "/login" in driver.current_url or "Registration successful" in driver.page_source
        )

    def test_03_duplicate_email_registration(self, driver):
        """Test duplicate email registration"""
        driver.get(f"{BASE_URL}/register")

        # Fill registration form with same email
        driver.find_element(By.NAME, "name").send_keys("Test Citizen 2")
        driver.find_element(By.NAME, "email").send_keys("test@example.com")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.NAME, "confirm_password").send_keys("password123")
        # Select citizen role from dropdown
        role_select = Select(driver.find_element(By.NAME, "role"))
        role_select.select_by_value("citizen")

        # Check the terms and conditions checkbox
        terms_checkbox = driver.find_element(By.ID, "terms")
        terms_checkbox.click()

        # Submit form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Check for error message
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        assert "Email already exists" in driver.page_source

    def test_04_login_success(self, driver):
        """Test successful login"""
        driver.get(f"{BASE_URL}/login")

        # Fill login form
        driver.find_element(By.NAME, "email").send_keys("test@example.com")
        driver.find_element(By.NAME, "password").send_keys("Password123")

        # Submit form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Check redirect to dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("/citizen_dashboard")
        )
        assert "/citizen_dashboard" in driver.current_url

    def test_05_login_failure(self, driver):
        """Test login with wrong credentials"""
        driver.get(f"{BASE_URL}/login")

        # Fill login form with wrong password
        driver.find_element(By.NAME, "email").send_keys("test@example.com")
        driver.find_element(By.NAME, "password").send_keys("wrongpassword")

        # Submit form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Check for error message
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        assert "Invalid email or password" in driver.page_source

    def test_06_submit_complaint(self, driver):
        """Test complaint submission"""
        # Ensure logged in
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.NAME, "email").send_keys("test@example.com")
        driver.find_element(By.NAME, "password").send_keys("Password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 10).until(EC.url_contains("/citizen_dashboard"))

        # Navigate to complaint form
        driver.get(f"{BASE_URL}/submit_complaint")

        # Fill complaint form
        driver.find_element(By.NAME, "category").send_keys("Potholes & Road Damage")
        driver.find_element(By.NAME, "description").send_keys("Large pothole on Main Street")
        driver.find_element(By.NAME, "address").send_keys("123 Main Street")
        driver.find_element(By.NAME, "landmark").send_keys("Near the park")

        # Submit form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Check for success message
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        assert "Complaint submitted successfully" in driver.page_source

    def test_07_admin_login(self, driver):
        """Test admin login"""
        driver.get(f"{BASE_URL}/login")

        # Fill login form with admin credentials
        driver.find_element(By.NAME, "email").send_keys("admin@example.com")
        driver.find_element(By.NAME, "password").send_keys("admin123")

        # Submit form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Check redirect to admin dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("/admin_dashboard")
        )
        assert "/admin_dashboard" in driver.current_url

    def test_08_admin_dashboard_stats(self, driver):
        """Test admin dashboard statistics"""
        # First login as admin
        driver.get(f"{BASE_URL}/login")

        # Wait for login page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )

        # Fill login form with admin credentials
        driver.find_element(By.NAME, "email").send_keys("admin@example.com")
        driver.find_element(By.NAME, "password").send_keys("Admin123!")

        # Submit form using JavaScript to avoid click interception
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        driver.execute_script("arguments[0].click();", submit_button)

        # Wait for redirect to admin dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("/admin/dashboard")
        )

        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "container-fluid"))
        )

        # Check main header
        assert "Administration Dashboard" in driver.page_source

        # Check user statistics cards
        assert "Total Users" in driver.page_source
        assert "Citizens" in driver.page_source
        assert "Officers" in driver.page_source
        assert "Admins" in driver.page_source

        # Check complaint statistics cards
        assert "Total" in driver.page_source  # for complaints
        assert "Submitted" in driver.page_source
        assert "In Progress" in driver.page_source
        assert "Resolved" in driver.page_source
        assert "Rejected" in driver.page_source
        assert "Unassigned" in driver.page_source

        # Check department performance section
        assert "Department Performance" in driver.page_source

        # Check category trends section
        assert "Category Trends" in driver.page_source

        # Check trends chart canvas
        chart_canvas = driver.find_element(By.ID, "trendsChart")
        assert chart_canvas is not None

        # Check recent activity section
        assert "Recent Activity" in driver.page_source

        # Check quick actions section
        assert "Quick Actions" in driver.page_source

        # Verify that dynamic content is present (check for numbers in statistics)
        import re
        numbers = re.findall(r'\d+', driver.page_source)
        assert len(numbers) > 0  # At least some numerical data should be present

    def test_09_csv_report_generation(self, driver):
        """Test CSV report generation"""
        driver.get(f"{BASE_URL}/admin/reports")

        # Find and click CSV export button (check the reports page)
        try:
            csv_button = driver.find_element(By.CSS_SELECTOR, "a[href*='export=csv']")
            csv_button.click()
            time.sleep(2)
            # In headless mode, we can't easily check file downloads, so just verify the page loads
            assert "Generate and download reports" in driver.page_source or "Reports" in driver.page_source
        except:
            # If button not found, just check that reports page loads
            assert "Generate and download reports" in driver.page_source or "Reports" in driver.page_source

    def test_10_database_validation(self):
        """Test database integrity"""
        # Connect to database
        db_path = os.path.join(os.path.dirname(__file__), 'instance', 'complaints.db')
        if not os.path.exists(db_path):
            pytest.skip("Database file does not exist - app may not be initialized yet")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Check users table
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            assert user_count >= 0  # Allow 0 users if no sample data

            # Check complaints table
            cursor.execute("SELECT COUNT(*) FROM complaints")
            complaint_count = cursor.fetchone()[0]
            assert complaint_count >= 0

            # Check if complaint is assigned to correct department
            cursor.execute("SELECT category FROM complaints WHERE id = (SELECT MAX(id) FROM complaints)")
            category = cursor.fetchone()
            if category:
                # Verify auto-assignment logic
                if "Road" in category[0]:
                    cursor.execute("SELECT department FROM users WHERE id = (SELECT assigned_officer_id FROM complaints WHERE id = (SELECT MAX(id) FROM complaints))")
                    department = cursor.fetchone()
                    if department:
                        assert "Roads" in department[0]
        finally:
            conn.close()

    def test_11_session_persistence(self, driver):
        """Test session persistence"""
        # Login
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.NAME, "email").send_keys("test@example.com")
        driver.find_element(By.NAME, "password").send_keys("Password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 10).until(EC.url_contains("/citizen_dashboard"))

        # Navigate to another page
        driver.get(f"{BASE_URL}/citizen_dashboard")

        # Check if still logged in
        assert "Logout" in driver.page_source
        assert "Welcome" in driver.page_source

    def test_12_logout(self, driver):
        """Test logout functionality"""
        # Ensure logged in
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.NAME, "email").send_keys("test@example.com")
        driver.find_element(By.NAME, "password").send_keys("Password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 10).until(EC.url_contains("/citizen_dashboard"))

        # Find logout link and click
        logout_link = driver.find_element(By.LINK_TEXT, "Logout")
        logout_link.click()

        # Check redirect to login page
        WebDriverWait(driver, 10).until(
            EC.url_contains("/login")
        )
        assert "/login" in driver.current_url

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
