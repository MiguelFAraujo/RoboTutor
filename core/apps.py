from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """Executa correções críticas no banco de dados ao iniciar o servidor."""
        # Importações locais para evitar erros de AppRegistryNotReady
        import os
        from django.conf import settings
        
        # Só rodamos isso em produção (ou se configurado)
        if os.getenv('VERCEL') == '1' or not settings.DEBUG:
            try:
                from django.contrib.sites.models import Site
                domain = 'robo-tutor.vercel.app'
                
                # Sincroniza o Site 1 (SITE_ID padrão)
                site, created = Site.objects.get_or_create(id=1, defaults={'domain': domain, 'name': 'RoboTutor'})
                if not created and site.domain != domain:
                    site.domain = domain
                    site.name = 'RoboTutor'
                    site.save()
                    print(f"✅ Startup: Database Site synchronized to {domain}")
            except Exception as e:
                # Falha silenciosa no startup se o banco não estiver pronto
                print(f"⚠️ Startup: Could not sync Site domain: {e}")
