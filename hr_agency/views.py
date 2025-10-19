from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def home(request):
    """Главная страница"""
    context = {}

    if request.user.is_authenticated:
        try:
            # Прямые импорты моделей
            import candidates.models as candidates_app
            import vacancies.models as vacancies_app

            candidates_count = candidates_app.Candidate.objects.count()
            vacancies_count = vacancies_app.Vacancy.objects.count()

            # Для Application может быть проблема с импортом
            try:
                responses_count = candidates_app.Application.objects.count()
            except:
                responses_count = 0

            context.update({
                'candidates_count': candidates_count,
                'vacancies_count': vacancies_count,
                'responses_count': responses_count,
            })

        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            # Значения по умолчанию
            context.update({
                'candidates_count': 0,
                'vacancies_count': 0,
                'responses_count': 0,
            })

    return render(request, 'home.html', context)

@login_required
def statistics(request):
    """Расширенная страница статистики"""
    try:
        from candidates.models import Candidate, Application
        from vacancies.models import Vacancy, Skill

        # Базовая статистика
        candidates_count = Candidate.objects.count()
        vacancies_count = Vacancy.objects.count()
        responses_count = Application.objects.count()

        # Статистика по статусам откликов
        pending_responses = Application.objects.filter(status='pending').count()
        approved_responses = Application.objects.filter(status='approved').count()
        rejected_responses = Application.objects.filter(status='rejected').count()

        # Самые популярные навыки
        from django.db.models import Count
        popular_skills = Skill.objects.annotate(
            candidate_count=Count('candidate'),
            vacancy_count=Count('vacancy')
        ).order_by('-candidate_count')[:10]

        # Статистика по вакансиям
        open_vacancies = Vacancy.objects.filter(status='open').count()
        closed_vacancies = Vacancy.objects.filter(status='closed').count()
        draft_vacancies = Vacancy.objects.filter(status='draft').count()

        # Последние отклики
        recent_applications = Application.objects.select_related('candidate', 'vacancy').order_by('-applied_date')[:5]

    except ImportError as e:
        # Резервные значения при ошибках импорта
        candidates_count = vacancies_count = responses_count = 0
        pending_responses = approved_responses = rejected_responses = 0
        popular_skills = []
        open_vacancies = closed_vacancies = draft_vacancies = 0
        recent_applications = []

    return render(request, 'statistics.html', {
        'candidates_count': candidates_count,
        'vacancies_count': vacancies_count,
        'responses_count': responses_count,
        'pending_responses': pending_responses,
        'approved_responses': approved_responses,
        'rejected_responses': rejected_responses,
        'popular_skills': popular_skills,
        'open_vacancies': open_vacancies,
        'closed_vacancies': closed_vacancies,
        'draft_vacancies': draft_vacancies,
        'recent_applications': recent_applications,
    })

@login_required
def profile(request):
    """Профиль пользователя"""
    return render(request, 'users/profile.html', {
        'user': request.user
    })

def register(request):
    """Регистрация нового пользователя"""
    messages.info(request, "Регистрация временно недоступна. Обратитесь к администратору.")
    return redirect('login')