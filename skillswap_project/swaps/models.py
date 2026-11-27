
from django.db import models
from django.contrib.auth.models import User
from skills.models import Skill


class SwapRequest(models.Model):

    STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('ACCEPTED', 'Accepted'),
    ('REJECTED', 'Rejected'),
    ('CANCELLED', 'Cancelled'),
    ('COMPLETED', 'Completed'),
]

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_requests'
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_requests'
    )

    requested_skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='requested_in_swaps'
    )

    offered_skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='offered_in_swaps'
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    sender_confirmed = models.BooleanField(default=False)
    receiver_confirmed = models.BooleanField(default=False)

    # Session details
    session_date = models.DateField(null=True, blank=True)
    session_time = models.TimeField(null=True, blank=True)

    meeting_platform = models.CharField(
        max_length=50,
        blank=True
    )

    meeting_link = models.URLField(blank=True)

    session_confirmed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}"
