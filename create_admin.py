from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@robotutor.com', 'admin') if not User.objects.filter(username='admin').exists() else None
