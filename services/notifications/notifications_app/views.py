from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter notifications by the current user's ID from the JWT token
        user_id = self.request.user.id
        return Notification.objects.filter(user_id=user_id)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        user_id = self.request.user.id
        Notification.objects.filter(user_id=user_id, is_read=False).update(is_read=True)
        return Response({'status': 'all notifications marked as read'})
