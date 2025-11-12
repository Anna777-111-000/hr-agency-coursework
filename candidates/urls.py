# candidates/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Основные URLs для кандидатов
    path('', views.candidate_list, name='candidate_list'),
    path('<int:candidate_id>/', views.candidate_detail, name='candidate_detail'),
    path('create/', views.candidate_create, name='candidate_create'),
    path('<int:candidate_id>/download-resume/', views.download_resume, name='download_resume'),
    path('<int:candidate_id>/attach-vacancy/', views.attach_candidate_to_vacancy, name='attach_candidate_to_vacancy'),
    path('<int:candidate_id>/edit/', views.candidate_edit, name='candidate_edit'),

    # Формы кадров
    path('personnel/form/', views.personnel_form, name='personnel_form'),
    path('personnel/forms/', views.personnel_form_list, name='personnel_form_list'),
    path('personnel/forms/<int:form_id>/', views.personnel_form_detail, name='personnel_form_detail'),
    path('personnel/forms/<int:form_id>/approve/', views.personnel_form_approve, name='personnel_form_approve'),
    path('personnel/forms/<int:form_id>/reject/', views.personnel_form_reject, name='personnel_form_reject'),

    # Только для администраторов
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.user_management, name='user_management'),
    path('admin/analytics/', views.candidate_analytics, name='candidate_analytics'),
    path('admin/settings/', views.system_settings, name='system_settings'),
    path('admin/export/', views.candidate_export, name='candidate_export'),

    # Менеджер
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('link-candidates/', views.link_candidates_to_forms, name='link_candidates'),
    path('personnel/forms/<int:candidate_id>/fill/', views.fill_personnel_form, name='fill_personnel_form'),
    path('personnel/candidates/', views.personnel_candidate_list, name='personnel_candidate_list'),
    # ДОБАВЬТЕ ЭТУ СТРОКУ ДЛЯ СИНХРОНИЗАЦИИ СТАТУСОВ:
    path('sync-statuses/', views.sync_all_statuses, name='sync_all_statuses'),

    # УДАЛИТЕ эту строку - она дублируется с hr_agency/urls.py
    # path('analytics/', views.recruitment_analytics, name='recruitment_analytics'),
]