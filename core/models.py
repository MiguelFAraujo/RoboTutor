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
    # Verifica se o profile existe antes de tentar salvar
    if hasattr(instance, 'profile'):
        try:
            instance.profile.save()
        except Exception:
            pass  # Profile ainda não existe, será criado pelo signal acima

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


class CatalogOrder(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_BLOCKED = "blocked"
    STATUS_FULFILLED = "fulfilled"
    STATUS_REFUNDED = "refunded"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendente"),
        (STATUS_PAID, "Pago"),
        (STATUS_BLOCKED, "Bloqueado"),
        (STATUS_FULFILLED, "Entregue"),
        (STATUS_REFUNDED, "Reembolsado"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="catalog_orders")
    pack_slug = models.CharField(max_length=80)
    pack_title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    amount_cents = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=8, default="brl")
    stripe_session_id = models.CharField(max_length=120, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=120, blank=True)
    customer_email = models.EmailField(blank=True)
    purchaser_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    risk_score = models.PositiveIntegerField(default=0)
    risk_reasons = models.JSONField(default=list, blank=True)
    source_snapshot = models.JSONField(default=dict, blank=True)
    delivery_bundle_path = models.CharField(max_length=500, blank=True)
    delivery_checksum = models.CharField(max_length=64, blank=True)
    downloaded_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.pack_title} - {self.user.username} ({self.status})"


class AuditEvent(models.Model):
    SEVERITY_INFO = "info"
    SEVERITY_WARNING = "warning"
    SEVERITY_CRITICAL = "critical"

    order = models.ForeignKey(CatalogOrder, on_delete=models.CASCADE, null=True, blank=True, related_name="events")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_events")
    event_type = models.CharField(max_length=80)
    severity = models.CharField(max_length=20, default=SEVERITY_INFO)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event_type} ({self.severity})"

