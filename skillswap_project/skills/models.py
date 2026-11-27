
from django.db import models
from django.contrib.auth.models import User


class SkillCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
    SkillCategory,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="skills"

    )

    def __str__(self):
        return self.name


class UserSkill(models.Model):

    SKILL_TYPE_CHOICES = [
        ('TEACH', 'I Can Teach'),
        ('LEARN', 'I Want to Learn'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    skill_type = models.CharField(
        max_length=10,
        choices=SKILL_TYPE_CHOICES
    )

    def __str__(self):
        return f"{self.user.username} - {self.skill.name} ({self.skill_type})"
