Church Management System (church_ms)

The Church Management System (church_ms) is a web-based application built with Django to manage church-related data, including provinces, districts, churches, worshipers, attendance, and news. It provides a user-friendly interface for administrators, main reverends, and pastors to oversee church operations, track membership, and manage announcements. The application supports internationalization (i18n) for multilingual support and uses Celery for asynchronous task processing.
Table of Contents

Features
Prerequisites
Installation
Configuration
Running the Application
Usage
Contributing
License
Contact

Features

User Authentication: Secure login/logout functionality with role-based access (Admin, Main Reverend, Pastor).
Location Management:
Manage provinces, districts, and churches with CRUD operations.
Assign main reverends to districts and pastors to churches.


Worshiper Management: Track worshiper details, including baptism status and gender distribution.
Attendance Tracking: Record and analyze church attendance data.
News Management: Create, edit, and delete news announcements, with asynchronous notifications via Celery.
Dashboard: Role-based dashboards displaying key metrics (e.g., number of churches, worshipers, attendance trends).
Multilingual Support: Built-in internationalization (i18n) for multiple languages.
Responsive Design: Bootstrap-based UI for a consistent experience across devices.
Asynchronous Tasks: Uses Celery with RabbitMQ/Redis for background task processing (e.g., notifications).

Prerequisites
Before setting up the project, ensure you have the following installed:

Python: 3.13 or higher
Django: 5.2 or higher
Message Broker: RabbitMQ or Redis (for Celery)
Database: SQLite (default) or PostgreSQL/MySQL (optional)
Git: For cloning the repository
pip: Python package manager
Virtualenv (recommended): For isolated Python environments

On Windows, you may need additional tools:

Erlang (for RabbitMQ)
RabbitMQ or a Redis Windows port (e.g., Memurai)

Installation
Follow these steps to set up the project locally:

Clone the Repository:
git clone (https://github.com/Kizito-Alberrt/Church-Management-System.git)
cd church_ms


Create a Virtual Environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:
pip install -r requirements.txt

Ensure requirements.txt includes:
django==5.2
celery==5.4.0
django-bootstrap5
kombu
# Add other dependencies as needed


Set Up the Message Broker:

RabbitMQ:
Install Erlang: Download
Install RabbitMQ: Download
Start RabbitMQ service:rabbitmq-service start




Redis (alternative):
Install Redis via WSL or a Windows port (e.g., Memurai).
Start Redis:redis-server






Apply Database Migrations:
python manage.py migrate


Create a Superuser (for admin access):
python manage.py createsuperuser



Configuration

Environment Variables:Create a .env file in the project root or update settings.py with the following:
SECRET_KEY=your-secret-key
DEBUG=True
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//  # or redis://localhost:6379/0
CELERY_RESULT_BACKEND=rpc://  # or redis://localhost:6379/0


Django Settings:Ensure settings.py includes:
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'church',
    'django_bootstrap5',
]

LANGUAGE_CODE = 'en-us'
USE_I18N = True
LOGIN_URL = 'church:login'


Celery Configuration:Verify church_ms/celery.py and church_ms/__init__.py are set up:
# church_ms/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_ms.settings')
app = Celery('church_ms')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# church_ms/__init__.py
from .celery import app as celery_app
__all__ = ('celery_app',)



Running the Application

Start the Message Broker:

RabbitMQ: Ensure the service is running (see Installation).
Redis: Run redis-server.


Start the Celery Worker:In a separate terminal, with the virtual environment activated:
celery -A church_ms worker --loglevel=info


Run the Django Development Server:
python manage.py runserver


Access the Application:Open your browser and navigate to http://127.0.0.1:8001/.


Usage

Admin Access: Log in at http://127.0.0.1:8001/admin/ using the superuser credentials.
Dashboard: After logging in, view role-based dashboards at http://127.0.0.1:8001/.
Manage Locations: Navigate to /provinces/, /districts/, or /churches/ to add, edit, or delete records.
News Management: Create or edit news at /news/create/ or /news/<id>/edit/.
Worshiper Tracking: View worshiper lists via /worshipers/ or church-specific links.
Logout: Log out at http://127.0.0.1:8001/logout/.

Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a new branch (git checkout -b feature/your-feature).
Make your changes and commit (git commit -m "Add your feature").
Push to the branch (git push origin feature/your-feature).
Open a Pull Request.

Please ensure your code follows PEP 8 style guidelines and includes tests where applicable.
License
This project is licensed under the MIT License. See the LICENSE file for details.


