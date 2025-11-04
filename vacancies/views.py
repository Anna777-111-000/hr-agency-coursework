from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vacancy, Skill
from .forms import VacancyForm, SkillForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def role_required(allowed_roles):
    """Декоратор для проверки ролей пользователя"""

    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            if hasattr(request.user, 'role') and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return render(request, '403.html', status=403)

        return wrapper

    return decorator


@login_required
def vacancy_list(request):
    vacancies_list = Vacancy.objects.all().order_by('-created_at')

    # Пагинация
    paginator = Paginator(vacancies_list, 10)
    page_number = request.GET.get('page', 1)  # Добавляем значение по умолчанию

    try:
        vacancies = paginator.page(page_number)
    except PageNotAnInteger:
        # Если page не integer, показываем первую страницу
        vacancies = paginator.page(1)
    except EmptyPage:
        # Если page вне диапазона, показываем последнюю страницу
        vacancies = paginator.page(paginator.num_pages)

    return render(request, 'vacancies/vacancy_list.html', {
        'vacancies': vacancies
    })


@role_required(['manager', 'admin'])
def vacancy_create(request):
    """Создание новой вакансии"""
    if request.method == 'POST':
        form = VacancyForm(request.POST, request=request)
        if form.is_valid():
            vacancy = form.save()
            messages.success(request, f'Вакансия "{vacancy.title}" успешно создана!')
            return redirect('vacancy_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = VacancyForm(request=request)

    return render(request, 'vacancies/vacancy_form.html', {
        'form': form,
        'title': 'Создать вакансию'
    })


@role_required(['manager', 'admin'])
def vacancy_edit(request, vacancy_id):
    """Редактирование вакансии"""
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)

    # Проверка прав - только создатель или администратор может редактировать
    if vacancy.created_by != request.user and request.user.role != 'admin':
        messages.error(request, "У вас нет прав для редактирования этой вакансии")
        return redirect('vacancy_list')

    if request.method == 'POST':
        form = VacancyForm(request.POST, instance=vacancy, request=request)
        if form.is_valid():
            vacancy = form.save()
            messages.success(request, f'Вакансия "{vacancy.title}" успешно обновлена!')
            return redirect('vacancy_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = VacancyForm(instance=vacancy, request=request)

    return render(request, 'vacancies/vacancy_form.html', {
        'form': form,
        'title': f'Редактировать вакансию: {vacancy.title}',
        'vacancy': vacancy
    })


@login_required
def vacancy_detail(request, vacancy_id):
    """Детальная страница вакансии"""
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)

    user_role = getattr(request.user, 'role', '')

    # УПРОЩЕННЫЕ ПРАВИЛА ДОСТУПА:
    # - Админы и менеджеры - доступ ко всем вакансиям
    # - Рекрутеры - доступ ко ВСЕМ вакансиям (и открытым, и закрытым)
    # - Остальные - только к открытым вакансиям

    if user_role not in ['manager', 'admin', 'recruiter']:
        # Для обычных пользователей - только открытые вакансии
        if vacancy.status != 'open':
            messages.error(request, "У вас нет прав для просмотра этой вакансии")
            return redirect('vacancy_list')

    # Получаем связанные заявки кандидатов
    applications_count = 0
    approved_applications = 0
    applications = []

    try:
        from candidates.models import Application
        applications = Application.objects.filter(vacancy=vacancy).select_related('candidate')
        applications_count = applications.count()
        approved_applications = applications.filter(status='approved').count()

        # Если рекрутер НЕ назначен на эту вакансию - показываем только его кандидатов
        if user_role == 'recruiter' and vacancy.assigned_recruiter != request.user:
            applications = applications.filter(candidate__assigned_recruiter=request.user.username)

    except Exception as e:
        print(f"Ошибка при загрузке заявок: {e}")

    return render(request, 'vacancies/vacancy_detail.html', {
        'vacancy': vacancy,
        'applications': applications,
        'applications_count': applications_count,
        'approved_applications': approved_applications,
        'user_role': user_role,
    })

@role_required(['manager', 'admin'])
def vacancy_delete(request, vacancy_id):
    """Удаление вакансии"""
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)

    # Проверка прав
    if vacancy.created_by != request.user and request.user.role != 'admin':
        messages.error(request, "У вас нет прав для удаления этой вакансии")
        return redirect('vacancy_list')

    if request.method == 'POST':
        vacancy_title = vacancy.title
        vacancy.delete()
        messages.success(request, f'Вакансия "{vacancy_title}" успешно удалена!')
        return redirect('vacancy_list')

    return render(request, 'vacancies/vacancy_confirm_delete.html', {
        'vacancy': vacancy
    })


@role_required(['manager', 'admin'])
def vacancy_change_status(request, vacancy_id, new_status):
    """Изменение статуса вакансии"""
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)

    # Проверка прав
    if vacancy.created_by != request.user and request.user.role != 'admin':
        messages.error(request, "У вас нет прав для изменения статуса этой вакансии")
        return redirect('vacancy_list')

    if new_status in ['open', 'closed', 'draft']:
        vacancy.status = new_status
        vacancy.save()

        status_display = dict(Vacancy.STATUS_CHOICES).get(new_status)
        messages.success(request, f'Статус вакансии "{vacancy.title}" изменен на "{status_display}"')

    return redirect('vacancy_detail', vacancy_id=vacancy_id)


@role_required(['manager', 'admin'])
def vacancy_change_status(request, vacancy_id, new_status):
    """Изменение статуса вакансии"""
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)

    # Проверка прав
    if vacancy.created_by != request.user and request.user.role != 'admin':
        messages.error(request, "У вас нет прав для изменения статуса этой вакансии")
        return redirect('vacancy_list')

    if new_status in ['open', 'closed', 'draft']:
        old_status = vacancy.status
        vacancy.status = new_status
        vacancy.save()

        status_display = dict(Vacancy.STATUS_CHOICES).get(new_status)
        old_status_display = dict(Vacancy.STATUS_CHOICES).get(old_status)
        messages.success(request,
                         f'Статус вакансии "{vacancy.title}" изменен с "{old_status_display}" на "{status_display}"')
    else:
        messages.error(request, "Неверный статус вакансии")

    return redirect('vacancy_detail', vacancy_id=vacancy_id)


@login_required
def skill_management(request):
    """Управление навыками - для менеджеров и администраторов"""
    if not hasattr(request.user, 'role') or request.user.role not in ['manager', 'admin']:
        messages.error(request, "У вас нет прав для управления навыками")
        return redirect('home')

    skills = Skill.objects.all().order_by('name')

    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Навык успешно создан!')
            return redirect('skill_management')
    else:
        form = SkillForm()

    return render(request, 'vacancies/skill_management.html', {
        'skills': skills,
        'form': form
    })


@login_required
def skill_edit(request, skill_id):
    """Редактирование навыка"""
    if not hasattr(request.user, 'role') or request.user.role not in ['manager', 'admin']:
        messages.error(request, "У вас нет прав для редактирования навыков")
        return redirect('home')

    skill = get_object_or_404(Skill, id=skill_id)

    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Навык успешно обновлен!')
            return redirect('skill_management')
    else:
        form = SkillForm(instance=skill)

    return render(request, 'vacancies/skill_edit.html', {
        'form': form,
        'skill': skill
    })


@login_required
def skill_delete(request, skill_id):
    """Удаление навыка"""
    if not hasattr(request.user, 'role') or request.user.role not in ['manager', 'admin']:
        messages.error(request, "У вас нет прав для удаления навыков")
        return redirect('home')

    skill = get_object_or_404(Skill, id=skill_id)

    if request.method == 'POST':
        skill_name = skill.name
        skill.delete()
        messages.success(request, f'Навык "{skill_name}" удален!')
        return redirect('skill_management')

    return render(request, 'vacancies/skill_confirm_delete.html', {
        'skill': skill
    })