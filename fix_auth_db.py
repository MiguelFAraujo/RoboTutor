
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robotutor_project.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# 1. Update Site Domain to match current port
site = Site.objects.get(id=2)
site.domain = 'localhost:8095'
site.name = 'RoboTutor Dev'
site.save()
print(f"Updated Site 2 to: {site.domain}")

# 2. Delete ALL SocialApps (conflicting with settings.py)
count = SocialApp.objects.count()
SocialApp.objects.all().delete()
print(f"Deleted {count} SocialApp(s) from database.")
print("Now relying on settings.py SOCIALACCOUNT_PROVIDERS['google']['APP'] configuration.")
