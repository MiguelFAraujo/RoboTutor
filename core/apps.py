import os
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        Sincroniza o Site e configura Google OAuth automaticamente.
        """
        # Evita executar durante comandos de migração
        import sys
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return
            
        try:
            from django.contrib.sites.models import Site
            
            is_vercel = os.getenv('VERCEL') == '1'
            domain = 'robo-tutor.vercel.app' if is_vercel else '127.0.0.1:8000'
            
            site, created = Site.objects.get_or_create(
                id=1,
                defaults={'domain': domain, 'name': 'RoboTutor'}
            )
            
            if not created and site.domain != domain:
                site.domain = domain
                site.name = 'RoboTutor'
                site.save()
                logger.info(f"Site synchronized: {domain}")
            
            # Configura Google OAuth automaticamente
            from .adapters import setup_google_oauth
            setup_google_oauth()
                
        except Exception as e:
            # Ignora erros durante migração ou se o banco não estiver pronto
            logger.debug(f"Setup error (ignorable): {e}")
