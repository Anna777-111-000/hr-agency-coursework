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


def role_required(allowed_roles):
    """Декоратор для проверки ролей пользователя"""

    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            if hasattr(request.user, 'role') and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "У вас нет прав для доступа к этой странице")
            return redirect('candidate_list')  # Перенаправляем вместо 403

        return wrapper

    return decorator


@login_required
def vacancy_detail(request, vacancy_id):
    """Детальная страница вакансии"""
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)

    # Проверяем права доступа
    user_role = getattr(request.user, 'role', '')

    # Разрешаем доступ:
    # - Менеджерам и админам всегда
    # - Рекрутерам, если они назначены на вакансию ИЛИ вакансия открыта
    # - Создателю вакансии
    if user_role not in ['manager', 'admin']:
        if vacancy.created_by != request.user:
            if user_role == 'recruiter':
                # Рекрутер может смотреть открытые вакансии ИЛИ назначенные ему
                if vacancy.status != 'open' and vacancy.assigned_recruiter != request.user:
                    messages.error(request, "У вас нет прав для просмотра этой вакансии")
                    return redirect('vacancy_list')
            else:
                # Остальные пользователи могут смотреть только открытые вакансии
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

        # Если рекрутер - показываем только кандидатов, которых он прикрепил
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
    paginator = Paginator(candidates_list, 12)  # 12 кандидатов на страницу
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

# Функции для форм - только менеджеры и админы
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
    """Список заполненных форм"""
    forms = PersonnelForm.objects.all()
    return render(request, 'candidates/personnel_form_list.html', {
        'forms': forms
    })

# Дополнительные функции для разных ролей
@role_required(['admin'])
def candidate_analytics(request):
    """Аналитика кандидатов - только для администраторов"""
    candidates = Candidate.objects.all()  # ИСПРАВЛЕНО: Candidate вместо PersonnelForm
    total_candidates = candidates.count()
    # Для Candidate нет поля is_approved, убираем эту статистику
    approved_candidates = 0

    return render(request, 'candidates/analytics.html', {
        'total_candidates': total_candidates,
        'approved_candidates': approved_candidates,
        'approval_rate': 0
    })

@role_required(['manager', 'admin'])
def candidate_export(request):
    """Экспорт данных кандидатов - для менеджеров и админов"""
    # Здесь будет логика экспорта данных
    return render(request, 'candidates/export.html')

@role_required(['admin'])
def system_settings(request):
    """Настройки системы - только для администраторов"""
    return render(request, 'candidates/settings.html')

@role_required(['admin'])
def user_management(request):
    """Управление пользователями"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    users = User.objects.all()

    if request.method == 'POST':
        # Обработка создания нового пользователя
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        email = request.POST.get('email')

        if username and password and role:
            try:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    role=role,
                    email=email or ''
                )
                messages.success(request, f'Пользователь {username} создан!')
            except Exception as e:
                messages.error(request, f'Ошибка: {e}')

    return render(request, 'admin/user_management.html', {
        'users': users
    })

@role_required(['admin'])
def create_user(request):
    """Быстрое создание пользователя"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        email = request.POST.get('email', '')

        if username and password and role:
            try:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    role=role,
                    email=email
                )
                return redirect('user_management')
            except Exception as e:
                # Обработка ошибки
                pass

    return render(request, 'admin/create_user.html')


@login_required
def manager_dashboard(request):
    """Панель управления для менеджеров"""
    # Проверка роли через атрибут пользователя
    if not hasattr(request.user, 'role') or request.user.role != 'manager':
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Доступ только для менеджеров")

    # Статистика кандидатов
    total_candidates = Candidate.objects.count()

    # Статистика вакансий
    from vacancies.models import Vacancy
    from django.contrib.auth import get_user_model
    User = get_user_model()

    total_vacancies = Vacancy.objects.count()
    open_vacancies = Vacancy.objects.filter(status='open').count()
    closed_vacancies = Vacancy.objects.filter(status='closed').count()

    # Статистика по формату работы
    office_vacancies = Vacancy.objects.filter(work_format='office').count()
    remote_vacancies = Vacancy.objects.filter(work_format='remote').count()
    hybrid_vacancies = Vacancy.objects.filter(work_format='hybrid').count()

    # Рекрутеры
    recruiters = User.objects.filter(role='recruiter')
    recruiters_count = recruiters.count()

    # Последние вакансии
    recent_vacancies = Vacancy.objects.all().order_by('-created_at')[:5]

    context = {
        'total_candidates': total_candidates,
        'total_vacancies': total_vacancies,
        'open_vacancies': open_vacancies,
        'closed_vacancies': closed_vacancies,
        'office_vacancies': office_vacancies,
        'remote_vacancies': remote_vacancies,
        'hybrid_vacancies': hybrid_vacancies,
        'recruiters': recruiters,
        'recruiters_count': recruiters_count,
        'recent_vacancies': recent_vacancies,
    }
    return render(request, 'manager/dashboard.html', context)

@role_required(['admin'])
def admin_dashboard(request):
    """Административная панель"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    users = User.objects.all()
    total_candidates = Candidate.objects.count()  # ИСПРАВЛЕНО: Candidate вместо PersonnelForm

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


@login_required
def schedule_interview(request, candidate_id):
    """Планирование собеседования"""
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if request.method == 'POST':
        interview_date = request.POST.get('interview_date')
        interview_type = request.POST.get('interview_type')
        notes = request.POST.get('notes', '')

        if not interview_date or not interview_type:
            messages.error(request, "Заполните все обязательные поля")
            return redirect('candidate_detail', candidate_id=candidate_id)

        try:
            # Преобразуем строку в datetime с учетом часового пояса
            from django.utils.timezone import make_aware
            import datetime

            naive_datetime = datetime.datetime.strptime(interview_date, '%Y-%m-%dT%H:%M')
            aware_datetime = make_aware(naive_datetime)

            # Создаем запись о собеседовании
            interview = Interview.objects.create(
                candidate=candidate,
                scheduled_date=aware_datetime,
                interview_type=interview_type,
                notes=notes,
                scheduled_by=request.user,
                status='scheduled'
            )

            formatted_date = aware_datetime.strftime('%d.%m.%Y в %H:%M')
            messages.success(request, f'Собеседование запланировано на {formatted_date}')

        except ValueError as e:
            messages.error(request, f"Неверный формат даты: {str(e)}")
        except Exception as e:
            messages.error(request, f"Ошибка при планировании: {str(e)}")

    return redirect('candidate_detail', candidate_id=candidate_id)

@login_required
def schedule_interview(request, candidate_id):
    """Планирование собеседования"""
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if request.method == 'POST':
        interview_date = request.POST.get('interview_date')
        interview_type = request.POST.get('interview_type')
        notes = request.POST.get('notes', '')

        if not interview_date or not interview_type:
            messages.error(request, "Заполните все обязательные поля")
            return redirect('candidate_detail', candidate_id=candidate_id)

        try:
            # Создаем запись о собеседовании
            from .models import Interview
            interview = Interview.objects.create(
                candidate=candidate,
                scheduled_date=interview_date,
                interview_type=interview_type,
                notes=notes,
                scheduled_by=request.user,
                status='scheduled'
            )

            messages.success(request, f'Собеседование запланировано на {interview_date}')

        except Exception as e:
            messages.error(request, f"Ошибка при планировании: {str(e)}")

    return redirect('candidate_detail', candidate_id=candidate_id)


# candidates/management/commands/send_interview_reminders.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from candidates.models import Interview
import datetime


class Command(BaseCommand):
    help = 'Отправляет напоминания о предстоящих собеседованиях'

    def handle(self, *args, **options):
        now = timezone.now()
        reminder_time = now + datetime.timedelta(hours=24)  # Напоминание за 24 часа

        # Находим собеседования, которые будут через 24 часа и напоминание еще не отправлено
        upcoming_interviews = Interview.objects.filter(
            scheduled_date__lte=reminder_time,
            scheduled_date__gt=now,
            status='scheduled',
            reminder_sent=False
        )

        for interview in upcoming_interviews:
            try:
                # Отправляем email напоминание
                subject = f'Напоминание: Собеседование с {interview.candidate}'
                message = f'''
Здравствуйте!

Напоминаем о запланированном собеседовании:

Кандидат: {interview.candidate.last_name} {interview.candidate.first_name} {interview.candidate.patronymic}
Должность: {interview.candidate.specialization or "Не указана"}
Дата и время: {interview.scheduled_date.strftime("%d.%m.%Y в %H:%M")}
Тип собеседования: {interview.get_interview_type_display()}
Заметки: {interview.notes or "Нет дополнительной информации"}

С уважением,
HR System
                '''

                # Отправляем email рекрутеру
                if interview.scheduled_by.email:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [interview.scheduled_by.email],
                        fail_silently=False,
                    )

                # Помечаем, что напоминание отправлено
                interview.reminder_sent = True
                interview.reminder_date = now
                interview.save()

                self.stdout.write(
                    self.style.SUCCESS(f'Напоминание отправлено для собеседования с {interview.candidate}')
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка при отправке напоминания: {e}')
                )