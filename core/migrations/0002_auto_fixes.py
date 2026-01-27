from django.db import migrations
from django.conf import settings

def fix_sites_and_profiles(apps, schema_editor):
    # --- FIX 1: SITE DOMAIN ---
    Site = apps.get_model('sites', 'Site')
    domain = 'robo-tutor.vercel.app'
    name = 'RoboTutor'
    
    # Brute force update ALL sites to the production domain
    # This ensures no matter what SITE_ID is used, it works
    if Site.objects.exists():
        for s in Site.objects.all():
            s.domain = domain
            s.name = name
            s.save()
            print(f"Updated Site {s.id} to {domain}")
    else:
        # Create at least one site if none exist (rare)
        Site.objects.create(domain=domain, name=name)
        print(f"Created Default Site")


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
