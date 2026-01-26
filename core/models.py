from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_premium = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} (Premium: {self.is_premium})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=100, default="Nova Conversa")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"

class MessageLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    role = models.CharField(max_length=10, default='user')
    content = models.TextField(default='') 
    timestamp = models.DateTimeField(auto_now_add=True)
    content_length = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"

class Project(models.Model):
    """User's saved projects collection"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True, related_name='project')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('in_progress', 'Em Progresso'),
        ('completed', 'Concluído'),
        ('paused', 'Pausado'),
    ], default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({self.user.username})"

