from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('chat', views.chat_api, name='chat'),
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
]
