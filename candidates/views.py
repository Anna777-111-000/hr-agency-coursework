from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Candidate
from .forms import PersonnelFormForm  # ДОБАВИТЬ ЭТОТ ИМПОРТ


def is_hr_user(user):
    """Проверка что пользователь относится к HR"""
    return user.is_authenticated and (user.is_staff or user.groups.filter(name='HR').exists())


@login_required
def candidate_list(request):
    """Список кандидатов с поиском и фильтрацией"""
    candidates = Candidate.objects.all()

    # Поиск по имени, фамилии или email
    search_query = request.GET.get('search', '')
    if search_query:
        candidates = candidates.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Фильтрация по опыту работы
    min_experience = request.GET.get('min_experience', '')
    if min_experience:
        try:
            candidates = candidates.filter(experience_years__gte=int(min_experience))
        except ValueError:
            pass

    return render(request, 'candidates/candidate_list.html', {
        'candidates': candidates,
        'search_query': search_query,
        'min_experience': min_experience
    })


@login_required
def candidate_detail(request, candidate_id):
    """Детальная страница кандидата"""
    candidate = get_object_or_404(Candidate, id=candidate_id)
    return render(request, 'candidates/candidate_detail.html', {
        'candidate': candidate
    })


# ДОБАВИТЬ НОВЫЕ ФУНКЦИИ ДЛЯ ФОРМЫ КАДРОВ
@login_required
def personnel_form(request):
    """Форма для отдела кадров"""
    if request.method == 'POST':
        form = PersonnelFormForm(request.POST)
        if form.is_valid():
            personnel_form = form.save()
            return render(request, 'candidates/personnel_form_success.html', {
                'personnel_form': personnel_form
            })
    else:
        form = PersonnelFormForm()

    return render(request, 'candidates/personnel_form.html', {
        'form': form
    })


@login_required
def personnel_form_list(request):
    """Список заполненных форм"""
    from .models import PersonnelForm  # Локальный импорт чтобы избежать циклических зависимостей
    forms = PersonnelForm.objects.all()
    return render(request, 'candidates/personnel_form_list.html', {
        'forms': forms
    })