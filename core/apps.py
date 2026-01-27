import os
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Sincronização automática do Site
        try:
            from django.contrib.sites.models import Site
            is_vercel = os.getenv('VERCEL') == '1'
            domain = 'robo-tutor.vercel.app' if is_vercel else '127.0.0.1:8000'
            
            site, created = Site.objects.get_or_create(id=1, defaults={'domain': domain, 'name': 'RoboTutor'})
            if not created and site.domain != domain:
                site.domain = domain
                site.save()
                logger.info(f"Site synchronized to: {domain}")
        except Exception:
            pass
            
        if os.getenv('VERCEL') != '1':
            return

        try:
            from django.contrib.sites.models import Site

            domain = 'robo-tutor.vercel.app'

            site, created = Site.objects.get_or_create(
                id=1,
                defaults={
                    'domain': domain,
                    'name': 'RoboTutor'
                }
            )

            if not created and site.domain != domain:
                site.domain = domain
                site.name = 'RoboTutor'
                site.save()

            logger.info(f"Site synchronized: {domain}")

        except Exception as e:
            logger.warning(f"Could not sync Site on startup: {e}")
