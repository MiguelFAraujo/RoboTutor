from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views, billing

urlpatterns = [
    path('', views.landing, name='landing'),
    path('chat/', views.index, name='index'),
    path('chat/', views.index, name='chat'),  # Alias for 'chat'
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/chat', views.chat_api, name='chat_api'),
    path('history/<int:conversation_id>/', views.get_conversation_history, name='history'),
    path('conversation/<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
    path('register/', views.register, name='register'),
    path('subscribe/', billing.create_checkout_session, name='subscribe'),
    path('webhook/', billing.stripe_webhook, name='webhook'),
    # path('accounts/', include('django.contrib.auth.urls')),
]

