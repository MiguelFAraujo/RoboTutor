from django.contrib.auth import views as auth_views
from . import views, billing

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('chat', views.chat_api, name='chat'),
    path('register/', views.register, name='register'),
    path('subscribe/', billing.create_checkout_session, name='subscribe'),
    path('webhook/', billing.stripe_webhook, name='webhook'),
    # path('accounts/', include('django.contrib.auth.urls')), # Desnecessário se definirmos login/logout explicito
]
