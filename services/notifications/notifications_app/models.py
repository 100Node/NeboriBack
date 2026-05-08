from django.db import models

class Notification(models.Model):
    user_id = models.IntegerField()  # Reference to User ID from Auth service
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for user {self.user_id}: {self.message[:20]}"
