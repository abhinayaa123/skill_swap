from django.urls import path
from .import views

urlpatterns=[
    path('add/', views.add_skill, name='add_skill'),
    path('browse/', views.browse_skills, name='browse_skills'),
    path('edit/<int:skill_id>/', views.edit_skill, name='edit_skill'),
    path('guest-browse/', views.guest_browse_skills, name='guest_browse_skills'),
    path('admin-browse/', views.admin_browse_skills, name='admin_browse_skills'),
]