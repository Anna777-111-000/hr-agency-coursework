from django.contrib import admin
from django.urls import path, include
from users import views as user_views

urlpatterns = [
    path('admin/', include('admin.urls')),
    path('', user_views.home, name='home'),
    path('candidates/', include('candidates.urls')),
    path('vacancies/', include('vacancies.urls')),
    path('users/', include('users.urls')),

]