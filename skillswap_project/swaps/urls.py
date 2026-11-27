
from django.urls import path
from . import views

urlpatterns = [
    path('send/<int:user_id>/<int:skill_id>/', views.send_swap_request, name='send_swap_request'),
    path('received/', views.received_requests, name='received_requests'),
    path(
        'update/<int:request_id>/<str:action>/',
        views.update_request_status,
        name='update_request_status'
    ),
    path(
    'my-swaps/',
    views.my_swaps,
    name='my_swaps'
),
    path(
    'sent/',
    views.sent_requests,
    name='sent_requests'
),
path(
    'confirm-completion/<int:request_id>/',
    views.confirm_completion,
    name='confirm_completion'
),

path(
    'schedule-session/<int:request_id>/',
    views.schedule_session,
    name='schedule_session'
),
path(
    'confirm-session/<int:request_id>/',
    views.confirm_session,
    name='confirm_session'
), 
path(
    'cancel/<int:request_id>/',
    views.cancel_request,
    name='cancel_request'
),
]
