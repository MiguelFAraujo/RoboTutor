
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robotutor_project.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

print("--- SITES ---")
for site in Site.objects.all():
    print(f"ID: {site.id} | Domain: {site.domain} | Name: {site.name}")

print("\n--- SOCIAL APPS ---")
for app in SocialApp.objects.all():
    print(f"ID: {app.id} | Provider: {app.provider} | Name: {app.name}")
    print(f"  -> Connected Sites: {[s.id for s in app.sites.all()]}")

from django.conf import settings
print(f"\nCURRENT SITE_ID SETTING: {settings.SITE_ID}")
