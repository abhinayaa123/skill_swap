
from django import forms
from .models import UserSkill


class UserSkillForm(forms.Form):

    skill = forms.CharField(max_length=100)

    category = forms.CharField(max_length=100)

    skill_type = forms.ChoiceField(
        choices=UserSkill.SKILL_TYPE_CHOICES
    )
