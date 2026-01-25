from django.db import models
from django.contrib.auth.models import User

class MessageLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    timestamp = models.DateTimeField(auto_now_add=True)
    content_length = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"
