from django import forms


class SessionForm(forms.Form):

    session_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    session_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'})
    )

    meeting_platform = forms.ChoiceField(
        choices=[
            ('Google Meet', 'Google Meet'),
            ('Zoom', 'Zoom'),
            ('Microsoft Teams', 'Microsoft Teams'),
            ('Other', 'Other'),
        ]
    )

    meeting_link = forms.URLField(
        required=False
    )