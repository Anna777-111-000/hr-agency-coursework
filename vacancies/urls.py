from django.urls import path
from . import views

urlpatterns = [
    path('', views.vacancy_list, name='vacancy_list'),
    path('create/', views.vacancy_create, name='vacancy_create'),
    path('<int:vacancy_id>/', views.vacancy_detail, name='vacancy_detail'),
    path('<int:vacancy_id>/edit/', views.vacancy_edit, name='vacancy_edit'),
    path('<int:vacancy_id>/delete/', views.vacancy_delete, name='vacancy_delete'),
    path('<int:vacancy_id>/status/<str:new_status>/', views.vacancy_change_status, name='vacancy_change_status'),
]