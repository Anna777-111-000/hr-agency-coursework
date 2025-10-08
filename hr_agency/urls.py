from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views
from candidates import views as candidate_views
from vacancies import views as vacancy_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    path('statistics/', views.statistics, name='statistics'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('candidates/', include('candidates.urls')),
    path('vacancies/', include('vacancies.urls')),
 ]
