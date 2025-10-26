from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    """Главная страница - разный контент для разных ролей"""
    return render(request, 'home.html')