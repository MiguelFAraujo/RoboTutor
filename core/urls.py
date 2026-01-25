from . import views, billing

urlpatterns = [
    path('', views.index, name='index'),
    path('chat', views.chat_api, name='chat'),
    path('register/', views.register, name='register'),
    path('subscribe/', billing.create_checkout_session, name='subscribe'),
    path('webhook/', billing.stripe_webhook, name='webhook'),
    path('accounts/', include('django.contrib.auth.urls')),
]
