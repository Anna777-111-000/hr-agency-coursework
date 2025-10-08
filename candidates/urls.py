from django.urls import path
from . import views

urlpatterns = [
    path('', views.candidate_list, name='candidate_list'),
    path('<int:candidate_id>/', views.candidate_detail, name='candidate_detail'),
    path('personnel-form/', views.personnel_form, name='personnel_form'),
    path('personnel-forms/', views.personnel_form_list, name='personnel_form_list'),
]