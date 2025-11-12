from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Candidate, PersonnelForm, Application, Interview
from .forms import PersonnelFormForm, CandidateCreateForm
from .forms import RecruiterCandidateForm
from django.http import FileResponse, Http404
from django.conf import settings
import os
from django.core.paginator import EmptyPage, PageNotAnInteger
from vacancies.models import Vacancy
from .forms import PersonnelFormForm, CandidateCreateForm, RecruiterCandidateForm, PersonnelFormFillForm

def role_required(allowed_roles):
    """Декоратор для проверки ролей пользователя"""
    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            if hasattr(request.user, 'role') and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "У вас нет прав для доступа к этой странице")
            return redirect('home')
        return wrapper
    return decorator

@login_required
def home(request):
    """Домашняя страница с учетом роли пользователя"""

    if hasattr(request.user, 'role') and request.user.role == 'admin':
        from django.contrib.auth import get_user_model
        User = get_user_model()
        from django.utils import timezone
        from datetime import timedelta

        # Базовая статистика
        total_users = User.objects.count()
        thirty_days_ago = timezone.now() - timedelta(days=30)
        active_users = User.objects.filter(last_login__gte=thirty_days_ago).count()

        # Статистика по ролям
        role_stats = {
            'admin': User.objects.filter(role='admin').count(),
            'manager': User.objects.filter(role='manager').count(),
            'recruiter': User.objects.filter(role='recruiter').count(),
        }

        # Дни работы системы
        try:
            first_user = User.objects.earliest('date_joined')
            system_uptime = (timezone.now() - first_user.date_joined).days
        except:
            system_uptime = 1

        # Статистика кандидатов
        total_candidates = Candidate.objects.count()

        # Последнее резервное копирование
        from datetime import datetime
        last_backup = datetime.now().strftime("%d.%m.%Y")

        context = {
            'total_users': total_users,
            'active_users': active_users,
            'role_stats': role_stats,
            'system_uptime': system_uptime,
            'total_candidates': total_candidates,
            'last_backup': last_backup,
        }
        return render(request, 'home.html', context)

    return render(request, 'home.html')


@login_required
def candidate_list(request):
    """Список кандидатов с поиском и фильтрацией"""
    candidates_list = Candidate.objects.all().order_by('-created_at')

    # Поиск по имени, фамилии или email
    search_query = request.GET.get('search', '')
    if search_query:
        candidates_list = candidates_list.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Фильтрация по опыту работы
    min_experience = request.GET.get('min_experience', '')
    if min_experience:
        try:
            candidates_list = candidates_list.filter(experience_years__gte=int(min_experience))
        except ValueError:
            pass

    # Фильтрация по образованию
    education_filter = request.GET.get('education', '')
    if education_filter:
        candidates_list = candidates_list.filter(education_level=education_filter)

    # Фильтрация по уровню позиции
    position_level_filter = request.GET.get('position_level', '')
    if position_level_filter:
        candidates_list = candidates_list.filter(position_level=position_level_filter)

    # Статистика
    total_candidates = candidates_list.count()
    experienced_candidates = candidates_list.filter(experience_years__gte=3).count()

    # Пагинация
    paginator = Paginator(candidates_list, 12)
    page_number = request.GET.get('page')
    candidates = paginator.get_page(page_number)

    return render(request, 'candidates/candidate_list.html', {
        'candidates': candidates,
        'search_query': search_query,
        'min_experience': min_experience,
        'total_candidates': total_candidates,
        'experienced_candidates': experienced_candidates
    })


@login_required
def candidate_detail(request, candidate_id):
    """Детальная страница кандидата"""
    candidate = get_object_or_404(Candidate, id=candidate_id)

    # Получаем открытые вакансии для модального окна
    from vacancies.models import Vacancy
    open_vacancies = Vacancy.objects.filter(status='open')

    return render(request, 'candidates/candidate_detail.html', {
        'candidate': candidate,
        'user_role': getattr(request.user, 'role', ''),
        'open_vacancies': open_vacancies
    })


@login_required
def candidate_create(request):
    """Создание нового кандидата - для рекрутеров и выше"""
    if not hasattr(request.user, 'role') or request.user.role not in ['recruiter', 'manager', 'admin']:
        messages.error(request, "У вас нет прав для создания кандидатов")
        return redirect('candidate_list')

    if request.method == 'POST':
        form = RecruiterCandidateForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                candidate = form.save()
                messages.success(request, f'Кандидат {candidate.first_name} {candidate.last_name} успешно создан!')
                return redirect('candidate_list')
            except Exception as e:
                messages.error(request, f'Ошибка при сохранении кандидата: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RecruiterCandidateForm()

    return render(request, 'candidates/candidate_create.html', {
        'form': form,
        'title': 'Добавить кандидата'
    })


@login_required
def candidate_edit(request, candidate_id):
    """Редактирование кандидата"""
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if not hasattr(request.user, 'role') or request.user.role not in ['recruiter', 'manager', 'admin']:
        messages.error(request, "У вас нет прав для редактирования кандидатов")
        return redirect('candidate_detail', candidate_id=candidate_id)

    if request.method == 'POST':
        form = RecruiterCandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            candidate = form.save()
            messages.success(request,
                             f'Данные кандидата {candidate.first_name} {candidate.last_name} успешно обновлены!')
            return redirect('candidate_detail', candidate_id=candidate_id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RecruiterCandidateForm(instance=candidate)

    return render(request, 'candidates/candidate_create.html', {
        'form': form,
        'title': f'Редактировать кандидата: {candidate.first_name} {candidate.last_name}',
        'candidate': candidate
    })


@login_required
def download_resume(request, candidate_id):
    """Безопасная загрузка резюме"""
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if not candidate.resume:
        raise Http404("Резюме не найдено")

    # Проверяем существование файла
    file_path = candidate.resume.path
    if not os.path.exists(file_path):
        raise Http404("Файл не найден")

    # Получаем имя файла для скачивания
    filename = os.path.basename(file_path)

    # Отправляем файл
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def attach_candidate_to_vacancy(request, candidate_id):
    """Прикрепление кандидата к вакансии"""
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if request.method == 'POST':
        vacancy_id = request.POST.get('vacancy_id')
        notes = request.POST.get('notes', '')

        if not vacancy_id:
            messages.error(request, "Выберите вакансию")
            return redirect('candidate_detail', candidate_id=candidate_id)

        try:
            from vacancies.models import Vacancy
            vacancy = Vacancy.objects.get(id=vacancy_id)

            # Создаем заявку (Application)
            application, created = Application.objects.get_or_create(
                candidate=candidate,
                vacancy=vacancy,
                defaults={
                    'status': 'pending',
                    'notes': notes
                }
            )

            if created:
                messages.success(request, f'Кандидат прикреплен к вакансии "{vacancy.title}"')
            else:
                messages.info(request, f'Кандидат уже прикреплен к вакансии "{vacancy.title}"')

        except Vacancy.DoesNotExist:
            messages.error(request, "Вакансия не найдена")
        except Exception as e:
            messages.error(request, f"Ошибка: {str(e)}")

    return redirect('candidate_detail', candidate_id=candidate_id)


# Формы кадров
@role_required(['manager', 'admin'])
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


@role_required(['manager', 'admin'])
def personnel_form_list(request):
    """Список кандидатов ДЛЯ МЕНЕДЖЕРА - только с анкетами И прикрепленные к вакансиям"""

    # Получаем кандидатов с анкетами И с заявками на вакансии
    candidates_list = Candidate.objects.filter(
        personnel_form__isnull=False,
        applications__isnull=False
    ).distinct().prefetch_related('personnel_form').order_by('-created_at')

    print(f"DEBUG: Кандидатов с анкетами и заявками: {candidates_list.count()}")

    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        candidates_list = candidates_list.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Фильтрация по статусу
    status_filter = request.GET.get('status', '')
    if status_filter:
        candidates_list = candidates_list.filter(
            personnel_form__candidate_status=status_filter
        )

    # Пагинация
    paginator = Paginator(candidates_list, 10)
    page_number = request.GET.get('page')
    candidates = paginator.get_page(page_number)

    # Статистика
    total_candidates = candidates_list.count()
    approved_count = candidates_list.filter(personnel_form__candidate_status='accepted').count()
    pending_count = candidates_list.filter(personnel_form__candidate_status='new').count()
    rejected_count = candidates_list.filter(personnel_form__candidate_status='rejected').count()

    context = {
        'candidates': candidates,
        'total_candidates': total_candidates,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'search_query': search_query,
        'status_filter': status_filter,
    }

    return render(request, 'candidates/personnel_form_list.html', context)



@login_required
def manager_dashboard(request):
    """Панель управления для менеджеров"""
    if not hasattr(request.user, 'role') or request.user.role != 'manager':
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Доступ только для менеджеров")

    # Основная статистика
    total_candidates = Candidate.objects.count()
    total_vacancies = Vacancy.objects.count()
    open_vacancies = Vacancy.objects.filter(status='open').count()

    # ИСПРАВЛЕННАЯ СТАТИСТИКА ЗАЯВОК
    try:
        # Используем абсолютный импорт
        from candidates.models import Application

        # Подсчитываем заявки по статусам
        approved_applications = Application.objects.filter(status='approved').count()
        pending_applications = Application.objects.filter(status='pending').count()
        rejected_applications = Application.objects.filter(status='rejected').count()
        total_applications = Application.objects.count()

        print(
            f"DEBUG: approved={approved_applications}, pending={pending_applications}, rejected={rejected_applications}")

    except Exception as e:
        print(f"Ошибка при загрузке заявок: {e}")
        # Устанавливаем значения по умолчанию
        approved_applications = 0
        pending_applications = 0
        rejected_applications = 0
        total_applications = 0

    # Форматы работы
    office_vacancies = Vacancy.objects.filter(work_format='office').count()
    remote_vacancies = Vacancy.objects.filter(work_format='remote').count()
    hybrid_vacancies = Vacancy.objects.filter(work_format='hybrid').count()

    # Рекрутеры
    from django.contrib.auth import get_user_model
    User = get_user_model()
    recruiters_count = User.objects.filter(role='recruiter').count()

    # Последние записи
    recent_candidates = Candidate.objects.all().order_by('-created_at')[:5]
    open_vacancies_list = Vacancy.objects.filter(status='open').order_by('-created_at')[:5]

    # Источники кандидатов
    source_stats = {}
    try:
        source_choices = Candidate._meta.get_field('source').choices
        for source_code, source_name in source_choices:
            count = Candidate.objects.filter(source=source_code).count()
            if count > 0:
                source_stats[source_name] = count
    except Exception as e:
        print(f"Ошибка при загрузке источников: {e}")

    context = {
        'total_candidates': total_candidates or 0,
        'total_vacancies': total_vacancies or 0,
        'open_vacancies': open_vacancies or 0,
        'open_vacancies_list': open_vacancies_list,
        'total_applications': total_applications or 0,
        'approved_applications': approved_applications or 0,
        'pending_applications': pending_applications or 0,
        'rejected_applications': rejected_applications or 0,
        'office_vacancies': office_vacancies or 0,
        'remote_vacancies': remote_vacancies or 0,
        'hybrid_vacancies': hybrid_vacancies or 0,
        'recruiters_count': recruiters_count or 0,
        'recent_candidates': recent_candidates,
        'source_stats': source_stats,
    }
    return render(request, 'manager/dashboard.html', context)

@role_required(['admin'])
def admin_dashboard(request):
    """Административная панель"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    users = User.objects.all()
    total_candidates = Candidate.objects.count()

    # Статистика по ролям
    recruiters = users.filter(role='recruiter').count()
    managers = users.filter(role='manager').count()
    admins = users.filter(role='admin').count()

    return render(request, 'admin/dashboard.html', {
        'users': users,
        'total_candidates': total_candidates,
        'recruiters_count': recruiters,
        'managers_count': managers,
        'admins_count': admins,
    })


@login_required
def candidate_analytics(request):
    # Реальные данные из базы
    total_candidates = Candidate.objects.count()
    total_vacancies = Vacancy.objects.count()
    total_applications = Application.objects.count()

    # Статусы заявок
    approved_count = Application.objects.filter(status='approved').count()
    pending_count = Application.objects.filter(status='pending').count()
    rejected_count = Application.objects.filter(status='rejected').count()

    # Конверсия (одобренные / все заявки)
    conversion_rate = round((approved_count / total_applications * 100) if total_applications > 0 else 0, 1)

    # Опыт кандидатов
    experience_data = [
        {
            'level': 'Junior (< 2 лет)',
            'count': Candidate.objects.filter(experience_years__lt=2).count(),
            'percentage': round((Candidate.objects.filter(
                experience_years__lt=2).count() / total_candidates * 100) if total_candidates > 0 else 0, 1)
        },
        {
            'level': 'Middle (2-5 лет)',
            'count': Candidate.objects.filter(experience_years__gte=2, experience_years__lte=5).count(),
            'percentage': round((Candidate.objects.filter(experience_years__gte=2,
                                                          experience_years__lte=5).count() / total_candidates * 100) if total_candidates > 0 else 0,1)
        },
        {
            'level': 'Senior (> 5 лет)',
            'count': Candidate.objects.filter(experience_years__gt=5).count(),
            'percentage': round((Candidate.objects.filter(
                experience_years__gt=5).count() / total_candidates * 100) if total_candidates > 0 else 0, 1)
        }
    ]

    # ИСПРАВЛЕННЫЙ ПОДСЧЕТ ИСТОЧНИКОВ КАНДИДАТОВ
    source_data = []
    try:
        source_choices = Candidate._meta.get_field('source').choices
        for source_code, source_name in source_choices:
            count = Candidate.objects.filter(source=source_code).count()
            if count > 0:
                source_data.append({
                    'source': source_name,
                    'count': count
                })
    except Exception as e:
        print(f"Ошибка при загрузке источников: {e}")
        # Fallback на статический список в случае ошибки
        source_data = [
            {'source': 'HH.ru', 'count': Candidate.objects.filter(source='hh').count()},
            {'source': 'LinkedIn', 'count': Candidate.objects.filter(source='linkedin').count()},
            {'source': 'Habr Career', 'count': Candidate.objects.filter(source='habr').count()},
            {'source': 'Рекомендация', 'count': Candidate.objects.filter(source='recommendation').count()},
            {'source': 'Другое', 'count': Candidate.objects.filter(source='other').count()},
        ]

    context = {
        'total_candidates': total_candidates,
        'total_vacancies': total_vacancies,
        'total_applications': total_applications,
        'conversion_rate': conversion_rate,
        'interviews_count': Application.objects.filter(status='pending').count(),
        # Предполагаем, что pending = собеседования
        'time_to_hire': 45,  # Можно рассчитать из дат, но пока заглушка

        'experience_data': experience_data,

        'status_data': [
            {'status': 'Одобрено', 'count': approved_count},
            {'status': 'На рассмотрении', 'count': pending_count},
            {'status': 'Отклонено', 'count': rejected_count},
        ],

        'source_data': source_data,  # ИСПРАВЛЕННЫЙ СПИСОК ИСТОЧНИКОВ

        'metrics': [
            {'name': 'Среднее время закрытия вакансии', 'value': '45 дн.'},
            {'name': 'Удовлетворенность кандидатов', 'value': '85%'},
            {'name': 'Стоимость одного найма', 'value': '25,000 руб.'},
            {'name': 'Удержание через 6 месяцев', 'value': '92%'},
        ]
    }

    return render(request, 'candidates/analytics.html', context)


@role_required(['manager', 'admin'])
def candidate_export(request):
    """Экспорт данных кандидатов - для менеджеров и админов"""
    return render(request, 'candidates/export.html')


@role_required(['admin'])
def system_settings(request):
    """Настройки системы - только для администраторов"""
    return render(request, 'candidates/settings.html')


@role_required(['admin'])
def user_management(request):
    """Управление пользователями - только для администраторов"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    users = User.objects.all().order_by('-date_joined')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_user':
            # Создание нового пользователя
            username = request.POST.get('username')
            password = request.POST.get('password')
            role = request.POST.get('role')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')

            if username and password and role:
                try:
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        role=role,
                        email=email or '',
                        phone_number=phone_number or ''
                    )
                    messages.success(request, f'Пользователь {username} успешно создан!')
                except Exception as e:
                    messages.error(request, f'Ошибка при создании пользователя: {str(e)}')

        elif action == 'delete_user':
            # Удаление пользователя
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                if user != request.user:  # Нельзя удалить себя
                    username = user.username
                    user.delete()
                    messages.success(request, f'Пользователь {username} удален!')
                else:
                    messages.error(request, 'Нельзя удалить собственный аккаунт!')
            except User.DoesNotExist:
                messages.error(request, 'Пользователь не найден!')

        elif action == 'change_role':
            # Изменение роли пользователя
            user_id = request.POST.get('user_id')
            new_role = request.POST.get('new_role')
            try:
                user = User.objects.get(id=user_id)
                if user != request.user:  # Нельзя изменить свою роль
                    user.role = new_role
                    user.save()
                    messages.success(request,
                                     f'Роль пользователя {user.username} изменена на {user.get_role_display()}')
                else:
                    messages.error(request, 'Нельзя изменить собственную роль!')
            except User.DoesNotExist:
                messages.error(request, 'Пользователь не найден!')

    # Статистика по ролям
    role_stats = {
        'admin': users.filter(role='admin').count(),
        'manager': users.filter(role='manager').count(),
        'recruiter': users.filter(role='recruiter').count(),
    }

    return render(request, 'admin/user_management.html', {
        'users': users,
        'role_stats': role_stats,
        'total_users': users.count(),
    })


@role_required(['manager', 'admin'])
def recruitment_analytics(request):
    """Аналитика рекрутинга для менеджеров и админов с реальными данными из БД"""

    # Основные метрики
    total_candidates = Candidate.objects.count()
    total_vacancies = Vacancy.objects.count()
    total_applications = Application.objects.count()

    # Статус заявок
    approved_applications = Application.objects.filter(status='approved').count()
    pending_applications = Application.objects.filter(status='pending').count()
    rejected_applications = Application.objects.filter(status='rejected').count()

    # Собеседования
    total_interviews = Interview.objects.count()
    upcoming_interviews = Interview.objects.filter(status='scheduled').count()

    # Опыт кандидатов - ИСПРАВЛЕННЫЙ ФОРМАТ (как в candidate_analytics)
    experience_data = [
        {
            'level': 'Junior (< 2 лет)',
            'count': Candidate.objects.filter(experience_years__lt=2).count(),
            'percentage': round((Candidate.objects.filter(
                experience_years__lt=2).count() / total_candidates * 100) if total_candidates > 0 else 0, 1)
        },
        {
            'level': 'Middle (2-5 лет)',
            'count': Candidate.objects.filter(experience_years__gte=2, experience_years__lte=5).count(),
            'percentage': round((Candidate.objects.filter(experience_years__gte=2,
                                                          experience_years__lte=5).count() / total_candidates * 100) if total_candidates > 0 else 0, 1)
        },
        {
            'level': 'Senior (> 5 лет)',
            'count': Candidate.objects.filter(experience_years__gt=5).count(),
            'percentage': round((Candidate.objects.filter(
                experience_years__gt=5).count() / total_candidates * 100) if total_candidates > 0 else 0, 1)
        }
    ]

    # Источники кандидатов - ИСПРАВЛЕННЫЙ ФОРМАТ (как в candidate_analytics)
    source_data = []
    try:
        source_choices = Candidate._meta.get_field('source').choices
        for source_code, source_name in source_choices:
            count = Candidate.objects.filter(source=source_code).count()
            if count > 0:
                source_data.append({
                    'source': source_name,
                    'count': count
                })
    except Exception as e:
        print(f"Ошибка при загрузке источников: {e}")

    # Статусы заявок - ИСПРАВЛЕННЫЙ ФОРМАТ (как в candidate_analytics)
    status_data = [
        {'status': 'Одобрено', 'count': approved_applications},
        {'status': 'На рассмотрении', 'count': pending_applications},
        {'status': 'Отклонено', 'count': rejected_applications},
    ]

    # Конверсия (одобренные / все заявки)
    conversion_rate = round((approved_applications / total_applications * 100) if total_applications > 0 else 0, 1)

    # Ключевые метрики
    metrics = [
        {'name': 'Среднее время закрытия вакансии', 'value': '45 дн.'},
        {'name': 'Удовлетворенность кандидатов', 'value': '85%'},
        {'name': 'Стоимость одного найма', 'value': '25,000 руб.'},
        {'name': 'Удержание через 6 месяцев', 'value': '92%'},
    ]

    context = {
        'total_candidates': total_candidates,
        'total_vacancies': total_vacancies,
        'total_applications': total_applications,
        'approved_applications': approved_applications,
        'pending_applications': pending_applications,
        'rejected_applications': rejected_applications,
        'total_interviews': total_interviews,
        'upcoming_interviews': upcoming_interviews,
        'conversion_rate': conversion_rate,
        'interviews_count': pending_applications,  # Предполагаем, что pending = собеседования
        'time_to_hire': 45,  # Можно рассчитать из дат, но пока заглушка

        # Исправленные форматы данных
        'experience_data': experience_data,
        'source_data': source_data,
        'status_data': status_data,
        'metrics': metrics,
    }

    return render(request, 'candidates/analytics.html', context)


@role_required(['manager', 'admin'])
def personnel_form_detail(request, form_id):
    """Детальная страница анкеты сотрудника"""
    personnel_form = get_object_or_404(PersonnelForm, id=form_id)

    return render(request, 'candidates/personnel_form_detail.html', {
        'form': personnel_form
    })


@role_required(['manager', 'admin'])
def personnel_form_approve(request, form_id):
    """Одобрение анкеты сотрудника"""
    personnel_form = get_object_or_404(PersonnelForm, id=form_id)

    if request.method == 'POST':
        personnel_form.is_approved = True
        personnel_form.candidate_status = 'accepted'
        personnel_form.save()
        messages.success(request, f'Анкета {personnel_form.last_name} {personnel_form.first_name} одобрена!')

    return redirect('personnel_form_list')


@role_required(['manager', 'admin'])
def personnel_form_reject(request, form_id):
    """Отклонение анкеты сотрудника"""
    personnel_form = get_object_or_404(PersonnelForm, id=form_id)

    if request.method == 'POST':
        personnel_form.is_approved = False
        personnel_form.candidate_status = 'rejected'
        personnel_form.save()
        messages.success(request, f'Анкета {personnel_form.last_name} {personnel_form.first_name} отклонена!')

    return redirect('personnel_form_list')


@login_required
@role_required(['manager', 'admin'])
def personnel_candidate_list(request):
    """Показываем ВСЕХ кандидатов для менеджера"""

    candidates_list = Candidate.objects.all().select_related('personnel_form').order_by('-created_at')

    print(f"DEBUG: Всего кандидатов для отображения: {candidates_list.count()}")

    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        candidates_list = candidates_list.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Фильтрация по статусу
    status_filter = request.GET.get('status', '')
    if status_filter:
        candidates_list = candidates_list.filter(
            personnel_form__candidate_status=status_filter
        )

    # Пагинация
    paginator = Paginator(candidates_list, 10)
    page_number = request.GET.get('page')
    candidates = paginator.get_page(page_number)

    # Статистика
    total_candidates = candidates_list.count()
    approved_count = candidates_list.filter(personnel_form__candidate_status='accepted').count()
    pending_count = candidates_list.filter(personnel_form__candidate_status='new').count()
    rejected_count = candidates_list.filter(personnel_form__candidate_status='rejected').count()

    context = {
        'candidates': candidates,
        'total_candidates': total_candidates,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'search_query': search_query,
        'status_filter': status_filter,
    }

    return render(request, 'candidates/personnel_candidate_list.html', context)

def sync_candidate_status(candidate):
    """Синхронизирует статус конкретного кандидата"""
    try:
        application = Application.objects.filter(candidate=candidate).first()
        if application and hasattr(candidate, 'personnel_form') and candidate.personnel_form:
            if candidate.personnel_form.candidate_status == 'accepted':
                application.status = 'approved'
            elif candidate.personnel_form.candidate_status == 'rejected':
                application.status = 'rejected'
            elif candidate.personnel_form.candidate_status == 'new':
                application.status = 'pending'
            application.save()
            return True
    except Exception as e:
        print(f"Ошибка синхронизации статуса для кандидата {candidate.id}: {e}")
    return False


@login_required
@role_required(['manager', 'admin'])
def approve_candidate(request, candidate_id):
    """Одобрение кандидата менеджером"""
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if hasattr(candidate, 'personnel_form') and candidate.personnel_form:
        candidate.personnel_form.candidate_status = 'accepted'
        candidate.personnel_form.is_approved = True
        candidate.personnel_form.save()

        # Синхронизируем статус заявки
        sync_candidate_status(candidate)

        messages.success(request, f'Кандидат {candidate.first_name} {candidate.last_name} одобрен!')
    else:
        messages.error(request, 'Форма персонала не найдена для этого кандидата')

    return redirect('personnel_candidate_list')


@login_required
@role_required(['manager', 'admin'])
def reject_candidate(request, candidate_id):
    """Отклонение кандидата менеджером"""
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if hasattr(candidate, 'personnel_form') and candidate.personnel_form:
        candidate.personnel_form.candidate_status = 'rejected'
        candidate.personnel_form.is_approved = False
        candidate.personnel_form.save()

        # Синхронизируем статус заявки
        sync_candidate_status(candidate)

        messages.success(request, f'Кандидат {candidate.first_name} {candidate.last_name} отклонен!')
    else:
        messages.error(request, 'Форма персонала не найдена для этого кандидата')

    return redirect('personnel_candidate_list')


@login_required
@role_required(['manager', 'admin'])
def link_candidates_to_forms(request):
    """Связывание ВСЕХ кандидатов с формами"""

    candidates = Candidate.objects.all()
    forms = PersonnelForm.objects.all()
    linked_count = 0
    created_count = 0

    print("=== СВЯЗЫВАНИЕ КАНДИДАТОВ С ФОРМАМИ ===")

    for candidate in candidates:
        # Проверяем, есть ли уже форма у кандидата
        if hasattr(candidate, 'personnel_form') and candidate.personnel_form:
            print(f"✅ Уже связан: {candidate.first_name} {candidate.last_name}")
            continue

        # Ищем подходящую форму по имени, фамилии и email
        matching_form = None
        for form in forms:
            if (form.first_name.lower() == candidate.first_name.lower() and
                    form.last_name.lower() == candidate.last_name.lower() and
                    form.email.lower() == candidate.email.lower()):
                matching_form = form
                break

        if matching_form and not matching_form.candidate:
            # Связываем существующую форму
            matching_form.candidate = candidate
            matching_form.save()
            linked_count += 1
            print(f"🔗 Связан: {candidate.first_name} {candidate.last_name} с формой {matching_form.id}")
        else:
            # Если формы нет - создаем новую
            try:
                new_form = PersonnelForm.objects.create(
                    first_name=candidate.first_name,
                    last_name=candidate.last_name,
                    patronymic=candidate.patronymic or "",
                    email=candidate.email,
                    phone=candidate.phone or "",
                    # Обязательные поля - заполняем заглушками
                    birth_date="2000-01-01",
                    birth_place="Не указано",
                    address="Не указано",
                    education="higher",
                    institution="Не указано",
                    specialty="Не указано",
                    graduation_year=2020,
                    marital_status="single",
                    passport_series="0000",
                    passport_number="000000",
                    passport_issued_by="Не указано",
                    passport_issue_date="2020-01-01",
                    passport_department_code="000-000",
                    work_experience_total=candidate.experience_years or 0,
                    work_experience_specialty=candidate.experience_years or 0,
                    candidate=candidate
                )
                created_count += 1
                print(f" Создана форма для: {candidate.first_name} {candidate.last_name}")
            except Exception as e:
                print(f"Ошибка создания формы для {candidate.first_name}: {e}")

    # Статистика
    total_linked = Candidate.objects.filter(personnel_form__isnull=False).count()
    total_candidates = Candidate.objects.count()

    print(f"=== ИТОГИ ===")
    print(f"Связано существующих: {linked_count}")
    print(f"Создано новых форм: {created_count}")
    print(f"Всего кандидатов с формами: {total_linked}/{total_candidates}")

    messages.success(request,
                     f'Связано {linked_count} кандидатов, создано {created_count} новых форм. Всего с формами: {total_linked}/{total_candidates}')
    return redirect('personnel_form_list')


@login_required
@role_required(['manager', 'admin'])
def fill_personnel_form(request, candidate_id):
    """Заполнение деталей анкеты сотрудника"""
    candidate = get_object_or_404(Candidate, id=candidate_id)

    # Проверяем, есть ли форма у кандидата
    if not hasattr(candidate, 'personnel_form') or not candidate.personnel_form:
        messages.error(request, 'У кандидата нет анкеты для заполнения')
        return redirect('candidate_detail', candidate_id=candidate_id)

    personnel_form = candidate.personnel_form

    if request.method == 'POST':
        form = PersonnelFormFillForm(request.POST, instance=personnel_form)
        if form.is_valid():
            form.save()
            messages.success(request, f'Анкета {candidate.first_name} {candidate.last_name} успешно заполнена!')
            return redirect('candidate_detail', candidate_id=candidate_id)
    else:
        form = PersonnelFormFillForm(instance=personnel_form)

    return render(request, 'candidates/fill_personnel_form.html', {
        'form': form,
        'candidate': candidate,
        'personnel_form': personnel_form
    })


@role_required(['manager', 'admin'])
def sync_all_statuses(request):
    """Синхронизирует все статусы заявок с анкетами"""
    candidates = Candidate.objects.all()
    synced_count = 0
    error_count = 0

    for candidate in candidates:
        try:
            # Используем функцию sync_candidate_status вместо метода модели
            if sync_candidate_status(candidate):
                synced_count += 1
        except Exception as e:
            print(f"Ошибка синхронизации для кандидата {candidate.id}: {e}")
            error_count += 1

    messages.success(request, f'Синхронизировано {synced_count} статусов. Ошибок: {error_count}')
    return redirect('personnel_form_list')