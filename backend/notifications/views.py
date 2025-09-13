from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

class NotificationDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

@api_view(['POST'])
def mark_as_read(request, pk):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(pk=pk, recipient=request.user)
        notification.mark_as_read()
        return Response({'message': 'Notification marquée comme lue'})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification non trouvée'}, status=404)

@api_view(['POST'])
def mark_all_as_read(request):
    """Mark all notifications as read"""
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return Response({'message': f'{count} notifications marquées comme lues'})

@api_view(['GET'])
def unread_count(request):
    """Get count of unread notifications"""
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return Response({'count': count})