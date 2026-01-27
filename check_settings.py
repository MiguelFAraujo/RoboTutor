
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robotutor_project.settings')
django.setup()

print(f"DEBUG: {settings.DEBUG}")
print(f"SECURE_SSL_REDIRECT: {getattr(settings, 'SECURE_SSL_REDIRECT', 'Not Set')}")
print(f"Loading .env file...")
from dotenv import load_dotenv
load_dotenv()
print(f"Env DEBUG: {os.getenv('DEBUG')}")
