# candidates/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Candidate, PersonnelForm
from .forms import PersonnelFormForm, CandidateCreateForm
from .forms import RecruiterCandidateForm
from django.http import FileResponse, Http404
from django.conf import settings
import os

def role_required(allowed_roles):
    """
    Декоратор для проверки ролей пользователя
    Использование: @role_required(['admin', 'manager'])
    """
    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            # Безопасная проверка роли
            if hasattr(request.user, 'role') and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            # Если нет прав - показываем ошибку
            return render(request, '403.html', status=403)
        return wrapper
    return decorator

def is_hr_user(user):
    """Проверка что пользователь относится к HR"""
    return user.is_authenticated and (user.is_staff or user.groups.filter(name='HR').exists())

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
    candidate = get_object_or_404(Candidate, id=candidate_id)  # ИСПРАВЛЕНО: Candidate вместо PersonnelForm

    return render(request, 'candidates/candidate_detail.html', {
        'candidate': candidate,
        'user_role': getattr(request.user, 'role', '')
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

    # Простая статистика
    total_candidates = Candidate.objects.count()  # ИСПРАВЛЕНО: Candidate вместо PersonnelForm

    context = {
        'total_candidates': total_candidates,
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