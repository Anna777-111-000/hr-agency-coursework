from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    """Кастомный выход с поддержкой GET запросов"""
    logout(request)
    return redirect('home')