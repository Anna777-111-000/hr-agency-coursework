from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Vacancy
from .forms import VacancyForm


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
    """Список вакансий с фильтрацией"""
    vacancies_list = Vacancy.objects.all().order_by('-created_at')

    # Фильтрация по статусу
    status_filter = request.GET.get('status', '')
    if status_filter:
        vacancies_list = vacancies_list.filter(status=status_filter)

    # Поиск по названию
    search_query = request.GET.get('search', '')
    if search_query:
        vacancies_list = vacancies_list.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Фильтрация по формату работы
    work_format_filter = request.GET.get('work_format', '')
    if work_format_filter:
        vacancies_list = vacancies_list.filter(work_format=work_format_filter)

    # Статистика
    total_vacancies = vacancies_list.count()
    open_vacancies = vacancies_list.filter(status='open').count()

    # Пагинация
    paginator = Paginator(vacancies_list, 10)
    page_number = request.GET.get('page')
    vacancies = paginator.get_page(page_number)

    return render(request, 'vacancies/vacancy_list.html', {
        'vacancies': vacancies,
        'search_query': search_query,
        'status_filter': status_filter,
        'work_format_filter': work_format_filter,
        'total_vacancies': total_vacancies,
        'open_vacancies': open_vacancies,
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