from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Candidate, PersonnelForm
from .forms import PersonnelFormForm


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
    """Список кандидатов с поиском и фильтрацией - доступно всем авторизованным"""

    # ИСПОЛЬЗУЕМ PersonnelForm вместо Candidate
    candidates = PersonnelForm.objects.all()

    print(f"DEBUG: Найдено кандидатов в БД: {candidates.count()}")
    for candidate in candidates:
        print(f"DEBUG: Кандидат: {candidate.last_name} {candidate.first_name}")

    # Поиск по имени, фамилии или email
    search_query = request.GET.get('search', '')
    if search_query:
        candidates = candidates.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Фильтрация по опыту работы (используем общий стаж)
    min_experience = request.GET.get('min_experience', '')
    if min_experience:
        try:
            candidates = candidates.filter(work_experience_total__gte=int(min_experience))
        except ValueError:
            pass

    return render(request, 'candidates/candidate_list.html', {
        'candidates': candidates,
        'search_query': search_query,
        'min_experience': min_experience
    })


@login_required
def candidate_detail(request, candidate_id):
    candidate = get_object_or_404(PersonnelForm, id=candidate_id)

    # Определяем уровень доступа по роли
    if request.user.role == 'admin':
        template = 'candidates/candidate_admin.html'
    elif request.user.role == 'manager':
        template = 'candidates/candidate_manager.html'
    else:  # recruiter
        template = 'candidates/candidate_public.html'

    return render(request, template, {
        'candidate': candidate,
        'user_role': request.user.role
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
    candidates = PersonnelForm.objects.all()
    total_candidates = candidates.count()
    approved_candidates = candidates.filter(is_approved=True).count()

    return render(request, 'candidates/analytics.html', {
        'total_candidates': total_candidates,
        'approved_candidates': approved_candidates,
        'approval_rate': (approved_candidates / total_candidates * 100) if total_candidates > 0 else 0
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
def admin_dashboard(request):
    """Административная панель"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    users = User.objects.all()
    total_candidates = PersonnelForm.objects.count()

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


@role_required(['admin'])
def user_management(request):
    """Управление пользователями"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    users = User.objects.all()

    if request.method == 'POST':
        # Обработка изменения ролей
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        if user_id and new_role:
            try:
                user = User.objects.get(id=user_id)
                user.role = new_role
                user.save()
            except User.DoesNotExist:
                pass

    return render(request, 'admin/user_management.html', {
        'users': users
    })


@role_required(['admin'])
def admin_dashboard(request):
    """Административная панель"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    users = User.objects.all()
    total_candidates = PersonnelForm.objects.count()

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
                # Сообщение об успехе
                from django.contrib import messages
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