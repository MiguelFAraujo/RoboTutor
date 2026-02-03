"""
Custom Adapter para django-allauth
Configura o Google OAuth automaticamente via variáveis de ambiente.
"""
import os
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from django.contrib.sites.models import Site


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adapter customizado que:
    1. Auto-conecta contas sociais a usuários existentes com mesmo email
    2. Melhora tratamento de erros
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Se já existe um usuário com o mesmo email, conecta automaticamente.
        """
        if sociallogin.is_existing:
            return
        
        email = sociallogin.account.extra_data.get('email')
        if email:
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(email=email)
                sociallogin.connect(request, user)
            except User.DoesNotExist:
                pass


def setup_google_oauth():
    """
    Configura o Google OAuth automaticamente usando variáveis de ambiente.
    Deve ser chamado no AppConfig.ready() após migrações.
    """
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("⚠️ GOOGLE_CLIENT_ID ou GOOGLE_CLIENT_SECRET não configurados")
        return False
    
    try:
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site
        
        # Obtém ou cria o site
        site, _ = Site.objects.get_or_create(
            id=1,
            defaults={'domain': 'robo-tutor.vercel.app', 'name': 'RoboTutor'}
        )
        
        # Obtém ou cria o SocialApp do Google
        app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': client_id,
                'secret': client_secret,
            }
        )
        
        # Atualiza se já existe mas credenciais mudaram
        if not created:
            if app.client_id != client_id or app.secret != client_secret:
                app.client_id = client_id
                app.secret = client_secret
                app.save()
        
        # Garante que o app está associado ao site
        if site not in app.sites.all():
            app.sites.add(site)
        
        print(f"✅ Google OAuth configurado para {site.domain}")
        return True
        
    except Exception as e:
        print(f"⚠️ Erro ao configurar Google OAuth: {e}")
        return False
