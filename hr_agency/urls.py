from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from candidates import views as candidate_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.home, name='home'),
    path('candidates/', include('candidates.urls')),
    path('vacancies/', include('vacancies.urls')),
    path('users/', include('users.urls')),
    path('manager/dashboard/', candidate_views.manager_dashboard, name='manager_dashboard'),
    path('admin/dashboard/', candidate_views.admin_dashboard, name='admin_dashboard'),

    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]