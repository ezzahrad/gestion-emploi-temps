from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = (
        ('schedule_change', 'Changement d\'emploi du temps'),
        ('absence', 'Absence déclarée'),
        ('makeup', 'Demande de rattrapage'),
        ('conflict', 'Conflit détecté'),
        ('reminder', 'Rappel'),
        ('system', 'Notification système'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('urgent', 'Urgente'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.full_name}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = models.DateTimeField(auto_now=True)
            self.save(update_fields=['is_read', 'read_at'])