from django.db import migrations
from django.conf import settings

def fix_sites_and_profiles(apps, schema_editor):
    import os
    # --- FIX 1: SITE DOMAIN ---
    Site = apps.get_model('sites', 'Site')
    domain = 'robo-tutor.vercel.app'
    name = 'RoboTutor'
    
    # Ensure Site 1 exists and is correct (matches SITE_ID=1)
    site, created = Site.objects.get_or_create(id=1, defaults={'domain': domain, 'name': name})
    if not created:
        site.domain = domain
        site.name = name
        site.save()
    
    # Also update any other sites to be sure
    for s in Site.objects.exclude(id=1):
        s.domain = domain
        s.name = name
        s.save()
    
    print(f"Sites synchronized to {domain}")

    # --- FIX 2: MISSING PROFILES ---
    User = apps.get_model(settings.AUTH_USER_MODEL)
    Profile = apps.get_model('core', 'Profile')
    
    users_fixed = 0
    for user in User.objects.all():
        if not Profile.objects.filter(user=user).exists():
            Profile.objects.create(user=user)
            users_fixed += 1
    
    if users_fixed > 0:
        print(f"Created {users_fixed} missing profiles.")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fix_sites_and_profiles),
    ]
