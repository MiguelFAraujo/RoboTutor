from django.db import migrations
from django.conf import settings

def fix_site_domain(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    # Tenta pegar o Site configurado no settings.SITE_ID (que é 2)
    # Se não existir, tenta o 1
    site_id = getattr(settings, 'SITE_ID', 1)
    
    if Site.objects.filter(id=site_id).exists():
        site = Site.objects.get(id=site_id)
        site.domain = 'robo-tutor.vercel.app'
        site.name = 'RoboTutor'
        site.save()
        print(f"Site {site_id} updated to robo-tutor.vercel.app")
    elif Site.objects.filter(id=1).exists():
        site = Site.objects.get(id=1)
        site.domain = 'robo-tutor.vercel.app'
        site.name = 'RoboTutor'
        site.save()
        print(f"Site 1 updated to robo-tutor.vercel.app")
    else:
        # Cria se não existir
        Site.objects.create(id=site_id, domain='robo-tutor.vercel.app', name='RoboTutor')
        print(f"Site {site_id} created")

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_project'),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fix_site_domain),
    ]
