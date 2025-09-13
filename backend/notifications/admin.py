from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient_name', 'notification_type_name', 'priority_name', 'is_read', 'is_sent', 'created_at_formatted')
    list_filter = ('notification_type', 'priority', 'is_read', 'is_sent', 'created_at')
    search_fields = ('title', 'message', 'recipient__first_name', 'recipient__last_name', 'recipient__email')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'read_at')
    
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'message', 'notification_type', 'priority')
        }),
        ('Destinataire', {
            'fields': ('recipient',)
        }),
        ('Statut', {
            'fields': ('is_read', 'is_sent', 'read_at')
        }),
        ('Métadonnées', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def recipient_name(self, obj):
        return obj.recipient.full_name
    recipient_name.short_description = 'Destinataire'
    
    def notification_type_name(self, obj):
        return obj.get_notification_type_display()
    notification_type_name.short_description = 'Type'
    
    def priority_name(self, obj):
        return obj.get_priority_display()
    priority_name.short_description = 'Priorité'
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_formatted.short_description = 'Créé le'
    
    # Actions personnalisées
    actions = ['mark_as_read', 'mark_as_unread', 'mark_as_sent']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notification(s) marquée(s) comme lue(s).')
    mark_as_read.short_description = 'Marquer comme lu'
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notification(s) marquée(s) comme non lue(s).')
    mark_as_unread.short_description = 'Marquer comme non lu'
    
    def mark_as_sent(self, request, queryset):
        updated = queryset.update(is_sent=True)
        self.message_user(request, f'{updated} notification(s) marquée(s) comme envoyée(s).')
    mark_as_sent.short_description = 'Marquer comme envoyé'
