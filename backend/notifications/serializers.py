from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source='recipient.full_name', read_only=True)
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('is_sent', 'read_at')
    
    def get_time_ago(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return "À l'instant"
        elif diff < timedelta(hours=1):
            return f"Il y a {diff.seconds // 60} min"
        elif diff < timedelta(days=1):
            return f"Il y a {diff.seconds // 3600} h"
        else:
            return f"Il y a {diff.days} jour(s)"