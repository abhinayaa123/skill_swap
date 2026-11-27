
from django.db import models
from django.contrib.auth.models import User
from swaps.models import SwapRequest
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q


class Review(models.Model):

    swap = models.ForeignKey(
        SwapRequest,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='given_reviews'
    )

    reviewed_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_reviews'
    )

    rating = models.PositiveIntegerField(
    validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ]
)

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['swap', 'reviewer'],
                name='unique_review_per_swap_reviewer'
            ),
            models.CheckConstraint(
                condition=Q(rating__gte=1, rating__lte=5),
                name='rating_between_1_and_5'
            )
        ]

    def __str__(self):
        return f"{self.reviewer.username} reviewed {self.reviewed_user.username}"