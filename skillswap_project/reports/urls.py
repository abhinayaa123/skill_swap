from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_report, name='submit_report'),
    path('my-reports/', views.my_reports, name='my_reports'),
    path('manage/', views.manage_reports, name='manage_reports'),
    path(
        'update-status/<int:report_id>/',
        views.update_report_status,
        name='update_report_status'
    ),
]