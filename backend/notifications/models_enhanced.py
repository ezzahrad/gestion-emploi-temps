from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json

User = get_user_model()

class Notification(models.Model):
    """Modèle étendu pour les notifications avancées"""
    NOTIFICATION_TYPE_CHOICES = (
        ('schedule_change', 'Changement d\'emploi du temps'),
        ('absence', 'Absence déclarée'),
        ('makeup', 'Demande de rattrapage'),
        ('conflict', 'Conflit détecté'),
        ('reminder', 'Rappel'),
        ('system', 'Notification système'),
        ('grade', 'Note publiée'),
        ('evaluation', 'Nouvelle évaluation'),
        ('pdf_export', 'Export PDF terminé'),
        ('attendance', 'Présence enregistrée'),
        ('admin_alert', 'Alerte administrative'),
        ('maintenance', 'Maintenance système'),
        ('security', 'Alerte sécurité'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('urgent', 'Urgente'),
        ('critical', 'Critique'),
    )
    
    DELIVERY_STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('sent', 'Envoyée'),
        ('delivered', 'Livrée'),
        ('failed', 'Échec'),
        ('read', 'Lue'),
    )
    
    # Informations de base (existantes)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # État et lecture
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    delivery_status = models.CharField(max_length=15, choices=DELIVERY_STATUS_CHOICES, default='pending')
    
    # Nouvelles fonctionnalités
    sender = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sent_notifications',
        help_text="Expéditeur de la notification"
    )
    
    # Canaux de livraison
    send_email = models.BooleanField(default=False)
    send_push = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=False)
    
    # Programmation
    scheduled_for = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Date/heure programmée pour l'envoi"
    )
    expires_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Date d'expiration de la notification"
    )
    
    # Action et interactivité
    action_url = models.URLField(blank=True, help_text="URL d'action pour la notification")
    action_text = models.CharField(max_length=100, blank=True, help_text="Texte du bouton d'action")
    requires_response = models.BooleanField(default=False)
    response_data = models.JSONField(default=dict, blank=True)
    
    # Groupement et catégories
    category = models.CharField(max_length=50, blank=True, help_text="Catégorie pour grouper les notifications")
    thread_id = models.CharField(max_length=100, blank=True, help_text="ID pour grouper des notifications liées")
    
    # Métadonnées étendues
    metadata = models.JSONField(default=dict, blank=True)
    template_data = models.JSONField(default=dict, blank=True, help_text="Données pour les templates")
    
    # Tracking et analytics
    email_opened = models.BooleanField(default=False)
    email_clicked = models.BooleanField(default=False)
    push_clicked = models.BooleanField(default=False)
    
    # Dates importantes
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type', 'created_at']),
            models.Index(fields=['priority', 'created_at']),
            models.Index(fields=['scheduled_for']),
            models.Index(fields=['thread_id']),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient.full_name}"

    def mark_as_read(self):
        """Marquer comme lue"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.delivery_status = 'read'
            self.save(update_fields=['is_read', 'read_at', 'delivery_status', 'updated_at'])

    def mark_as_sent(self):
        """Marquer comme envoyée"""
        self.is_sent = True
        self.sent_at = timezone.now()
        self.delivery_status = 'sent'
        self.save(update_fields=['is_sent', 'sent_at', 'delivery_status', 'updated_at'])

    def is_expired(self):
        """Vérifier si la notification a expiré"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def can_be_sent(self):
        """Vérifier si la notification peut être envoyée"""
        if self.is_expired():
            return False
        if self.scheduled_for and timezone.now() < self.scheduled_for:
            return False
        return True

    def get_display_time(self):
        """Obtenir le temps d'affichage relatif"""
        from django.utils.timesince import timesince
        return timesince(self.created_at)

class NotificationTemplate(models.Model):
    """Templates pour les notifications"""
    name = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=20, choices=Notification.NOTIFICATION_TYPE_CHOICES)
    
    # Templates pour différents formats
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    email_subject_template = models.CharField(max_length=200, blank=True)
    email_body_template = models.TextField(blank=True)
    sms_template = models.CharField(max_length=160, blank=True)
    push_template = models.TextField(blank=True)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    default_priority = models.CharField(max_length=10, choices=Notification.PRIORITY_CHOICES, default='medium')
    
    # Canaux par défaut
    default_send_email = models.BooleanField(default=False)
    default_send_push = models.BooleanField(default=True)
    default_send_sms = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['notification_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_notification_type_display()})"

    def render_title(self, context):
        """Rendre le titre avec le contexte"""
        from django.template import Template, Context
        template = Template(self.title_template)
        return template.render(Context(context))

    def render_message(self, context):
        """Rendre le message avec le contexte"""
        from django.template import Template, Context
        template = Template(self.message_template)
        return template.render(Context(context))

class NotificationSettings(models.Model):
    """Paramètres de notification par utilisateur"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    
    # Canaux globaux
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Paramètres par type de notification
    schedule_changes = models.BooleanField(default=True)
    absence_reminders = models.BooleanField(default=True)
    grade_updates = models.BooleanField(default=True)
    system_announcements = models.BooleanField(default=True)
    makeup_requests = models.BooleanField(default=True)
    pdf_exports = models.BooleanField(default=True)
    
    # Horaires de réception
    quiet_hours_start = models.TimeField(default='22:00')
    quiet_hours_end = models.TimeField(default='07:00')
    weekend_notifications = models.BooleanField(default=False)
    
    # Fréquence des résumés
    daily_digest = models.BooleanField(default=False)
    weekly_digest = models.BooleanField(default=True)
    
    # Paramètres avancés
    auto_mark_read_after_days = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(365)]
    )
    group_similar_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Paramètres de {self.user.full_name}"

    @classmethod
    def get_or_create_for_user(cls, user):
        """Obtenir ou créer les paramètres pour un utilisateur"""
        settings, created = cls.objects.get_or_create(user=user)
        return settings

    def should_send_notification(self, notification_type, channel='push'):
        """Vérifier si une notification doit être envoyée"""
        # Vérifier les canaux globaux
        if channel == 'email' and not self.email_notifications:
            return False
        elif channel == 'push' and not self.push_notifications:
            return False
        elif channel == 'sms' and not self.sms_notifications:
            return False
        
        # Vérifier les types spécifiques
        type_settings = {
            'schedule_change': self.schedule_changes,
            'absence': self.absence_reminders,
            'grade': self.grade_updates,
            'evaluation': self.grade_updates,
            'system': self.system_announcements,
            'makeup': self.makeup_requests,
            'pdf_export': self.pdf_exports,
        }
        
        return type_settings.get(notification_type, True)

    def is_in_quiet_hours(self):
        """Vérifier si nous sommes dans les heures silencieuses"""
        now = timezone.now().time()
        
        if self.quiet_hours_start <= self.quiet_hours_end:
            # Même jour (ex: 22:00 à 07:00 du lendemain)
            return now >= self.quiet_hours_start or now <= self.quiet_hours_end
        else:
            # Plage normale (ex: 08:00 à 18:00)
            return self.quiet_hours_start <= now <= self.quiet_hours_end

class NotificationGroup(models.Model):
    """Groupes de notifications pour les envois en masse"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Critères de sélection
    user_roles = models.JSONField(default=list, help_text="Rôles d'utilisateurs ciblés")
    departments = models.JSONField(default=list, help_text="IDs des départements")
    programs = models.JSONField(default=list, help_text="IDs des programmes")
    
    # Configuration
    is_active = models.BooleanField(default=True)
    auto_add_new_users = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_recipients(self):
        """Obtenir la liste des destinataires du groupe"""
        from django.db.models import Q
        
        query = Q()
        
        # Filtrer par rôles
        if self.user_roles:
            query |= Q(role__in=self.user_roles)
        
        # Filtrer par départements
        if self.departments:
            query |= Q(department__in=self.departments)
        
        # Filtrer par programmes
        if self.programs:
            query |= Q(program__in=self.programs)
        
        return User.objects.filter(query, is_active=True)

class NotificationBatch(models.Model):
    """Envoi en masse de notifications"""
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=Notification.NOTIFICATION_TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=Notification.PRIORITY_CHOICES, default='medium')
    
    # Ciblage
    target_groups = models.ManyToManyField(NotificationGroup, blank=True)
    target_users = models.ManyToManyField(User, blank=True)
    
    # Configuration
    send_email = models.BooleanField(default=False)
    send_push = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=False)
    
    # Programmation
    scheduled_for = models.DateTimeField(null=True, blank=True)
    
    # Statut
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Brouillon'),
        ('scheduled', 'Programmé'),
        ('sending', 'Envoi en cours'),
        ('sent', 'Envoyé'),
        ('failed', 'Échec'),
    ], default='draft')
    
    # Statistiques
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    read_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    
    # Métadonnées
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_batches')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.total_recipients} destinataires)"

    def calculate_recipients(self):
        """Calculer le nombre de destinataires"""
        recipients = set()
        
        # Ajouter les utilisateurs des groupes
        for group in self.target_groups.all():
            recipients.update(group.get_recipients())
        
        # Ajouter les utilisateurs individuels
        recipients.update(self.target_users.all())
        
        self.total_recipients = len(recipients)
        self.save(update_fields=['total_recipients'])
        
        return list(recipients)

class NotificationDeliveryLog(models.Model):
    """Log de livraison des notifications"""
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='delivery_logs')
    
    # Canal et statut
    channel = models.CharField(max_length=10, choices=[
        ('push', 'Push'),
        ('email', 'Email'),
        ('sms', 'SMS'),
    ])
    status = models.CharField(max_length=15, choices=Notification.DELIVERY_STATUS_CHOICES)
    
    # Détails de livraison
    provider_id = models.CharField(max_length=100, blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.notification.title} - {self.channel} ({self.status})"
