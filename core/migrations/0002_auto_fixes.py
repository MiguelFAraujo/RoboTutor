from django.db import migrations
from django.conf import settings

def fix_sites_and_profiles(apps, schema_editor):
    import os
    # --- FIX 1: SITE DOMAIN ---
    Site = apps.get_model('sites', 'Site')
    domain = 'robo-tutor.vercel.app'
    name = 'RoboTutor'
    
    # Ensure Site 1 exists and is correct
    site, created = Site.objects.get_or_create(id=1, defaults={'domain': domain, 'name': name})
    if not created:
        site.domain = domain
        site.name = name
        site.save()
    print(f"Site 1 sync: {domain}")

    # --- FIX 2: SOCIAL APP (GOOGLE) ---
    # We must ensure the SocialApp exists in DB and is linked to the Site
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    secret = os.getenv('GOOGLE_CLIENT_SECRET', '')
    
    if client_id and secret:
        app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google Login',
                'client_id': client_id,
                'secret': secret,
            }
        )
        if not created:
            app.client_id = client_id
            app.secret = secret
            app.save()
        
        # Link to the current site
        app.sites.add(site)
        print(f"SocialApp 'google' synced and linked to Site 1")


    # --- FIX 3: MISSING PROFILES ---
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
        ('socialaccount', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fix_sites_and_profiles),
    ]
