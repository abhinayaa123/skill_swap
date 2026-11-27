from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ['rating', 'comment']

        widgets = {
            'rating': forms.Select(
                choices=[
                    (1, '1 - Poor'),
                    (2, '2 - Fair'),
                    (3, '3 - Good'),
                    (4, '4 - Very Good'),
                    (5, '5 - Excellent'),
                ]
            ),
            'comment': forms.Textarea(attrs={
                'placeholder': 'Share your experience...'
            })
        }