from django.db import migrations
from django.conf import settings

def fix_all_sites(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    
    # Update ALL sites to the correct domain to avoid any confusion
    # This is a brute-force fix for the "Site mismatch" error
    domain = 'robo-tutor.vercel.app'
    name = 'RoboTutor'
    
    # Update default site (ID 2 or settings.SITE_ID)
    primary_id = getattr(settings, 'SITE_ID', 2)
    
    if Site.objects.filter(id=primary_id).exists():
        s = Site.objects.get(id=primary_id)
        s.domain = domain
        s.name = name
        s.save()
        print(f"Updated Primary Site {primary_id}")
    else:
        Site.objects.create(id=primary_id, domain=domain, name=name)
        print(f"Created Primary Site {primary_id}")

    # Also fix ID 1 just in case, or any other site
    for s in Site.objects.exclude(id=primary_id):
        s.domain = domain
        s.name = name
        s.save()
        print(f"Updated Secondary Site {s.id}")

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_fix_missing_profiles'),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fix_all_sites),
    ]
