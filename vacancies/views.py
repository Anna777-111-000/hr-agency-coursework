from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Vacancy

@login_required
def vacancy_list(request):
    """Список вакансий"""
    vacancies = Vacancy.objects.all()
    return render(request, 'vacancies/vacancy_list.html', {'vacancies': vacancies})