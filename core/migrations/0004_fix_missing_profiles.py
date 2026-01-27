from django.db import migrations

def create_missing_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('core', 'Profile')
    
    users_without_profile = 0
    for user in User.objects.all():
        if not Profile.objects.filter(user=user).exists():
            Profile.objects.create(user=user, is_premium=False)
            users_without_profile += 1
            print(f"Created missing profile for user: {user.username}")
    
    print(f"Total profiles created: {users_without_profile}")

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_fix_site_domain'),
    ]

    operations = [
        migrations.RunPython(create_missing_profiles),
    ]
