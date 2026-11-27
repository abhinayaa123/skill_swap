from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('toggle-user/<int:user_id>/', views.toggle_user_status, name='toggle_user_status' ),
    path('manage-skills/', views.manage_skills, name='manage_skills'),
    path('delete-skill/<int:skill_id>/', views.delete_user_skill, name='delete_user_skill'),
    
]