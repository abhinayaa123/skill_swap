
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q

from .models import IssueReport
from swaps.models import SwapRequest


class IssueReportForm(forms.ModelForm):

    class Meta:
        model = IssueReport
        fields = ['reported_user', 'title', 'description']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            completed_swaps = SwapRequest.objects.filter(
                status='COMPLETED'
            ).filter(
                Q(sender=user) | Q(receiver=user)
            )

            sender_ids = completed_swaps.filter(
                sender=user
            ).values_list('receiver_id', flat=True)

            receiver_ids = completed_swaps.filter(
                receiver=user
            ).values_list('sender_id', flat=True)

            other_user_ids = list(sender_ids) + list(receiver_ids)

            already_reported_ids = IssueReport.objects.filter(
                reported_by=user
            ).values_list('reported_user_id', flat=True)

            self.fields['reported_user'].queryset = User.objects.filter(
                id__in=other_user_ids
            ).exclude(
                id__in=already_reported_ids
            ).distinct()
