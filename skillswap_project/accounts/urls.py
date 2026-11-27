
from django.urls import path
from . import views


urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.user_login, name="user_login"),
    path("logout/", views.user_logout, name="user_logout"),
    path("profile/", views.profile, name="profile"),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("user/<int:user_id>/", views.view_user_profile, name="view_user_profile"),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('home/', views.user_home, name='user_home'),
    
   
]
