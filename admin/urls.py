from django.urls import path
from . import views

app_name = 'admin'

urlpatterns = [
    path('', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('users/create/', views.create_user, name='create_user'),

    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
]