from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('candidates/', include('candidates.urls')),
    path('vacancies/', include('vacancies.urls')),
    path('users/', include('users.urls')),
    path('statistics/', views.statistics, name='statistics'),
]