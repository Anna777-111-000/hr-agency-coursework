from django.urls import path
from . import views

urlpatterns = [
    # Основные URLs для кандидатов
    path('', views.candidate_list, name='candidate_list'),
    path('<int:candidate_id>/', views.candidate_detail, name='candidate_detail'),

    # Формы кадров
    path('personnel/form/', views.personnel_form, name='personnel_form'),
    path('personnel/forms/', views.personnel_form_list, name='personnel_form_list'),

    # Только для администраторов
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.user_management, name='user_management'),
    path('admin/analytics/', views.candidate_analytics, name='candidate_analytics'),
    path('admin/settings/', views.system_settings, name='system_settings'),
    path('admin/export/', views.candidate_export, name='candidate_export'),
]