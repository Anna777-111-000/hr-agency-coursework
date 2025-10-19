from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import User
from django.contrib import messages


def is_superadmin(user):
    """Проверяет, является ли пользователь суперадмином"""
    return user.is_authenticated and user.username == 'systemadmin'


@login_required
def superadmin_dashboard(request):
    # Только суперадмин имеет доступ
    if not is_superadmin(request.user):
        messages.error(request, 'Доступ запрещен')
        return redirect('home')

    # Статистика пользователей
    total_users = User.objects.exclude(username='systemadmin').count()
    managers_count = User.objects.filter(role='manager').count()
    recruiters_count = User.objects.filter(role='recruiter').count()

    context = {
        'total_users': total_users,
        'managers_count': managers_count,
        'recruiters_count': recruiters_count,
    }

    return render(request, 'admin/superadmin_dashboard.html', context)


@login_required
def user_management(request):
    # Только суперадмин имеет доступ
    if not is_superadmin(request.user):
        messages.error(request, 'Доступ запрещен')
        return redirect('home')

    # Обработка создания пользователя
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        email = request.POST.get('email', '')

        # Проверяем, что пользователь не существует
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Пользователь {username} уже существует')
        else:
            # Создаем пользователя
            try:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    role=role,
                    email=email
                )
                messages.success(request, f'Пользователь {username} успешно создан!')
            except Exception as e:
                messages.error(request, f'Ошибка при создании пользователя: {e}')

    users = User.objects.exclude(username='systemadmin')  # Все пользователи кроме суперадмина

    # Статистика по ролям
    managers_count = users.filter(role='manager').count()
    recruiters_count = users.filter(role='recruiter').count()
    admins_count = users.filter(role='administrator').count()

    context = {
        'users': users,
        'managers_count': managers_count,
        'recruiters_count': recruiters_count,
        'admins_count': admins_count,
    }

    return render(request, 'admin/user_management.html', context)


@login_required
def create_user(request):
    if not is_superadmin(request.user):
        messages.error(request, 'Доступ запрещен')
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        email = request.POST.get('email', '')
        phone_number = request.POST.get('phone_number', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        print(f"DEBUG: Создание пользователя - {username}, {role}, {email}, {phone_number}, {first_name} {last_name}")

        if User.objects.filter(username=username).exists():
            messages.error(request, f'Пользователь {username} уже существует')
            print(f"DEBUG: Пользователь {username} уже существует")
        else:
            try:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    role=role,
                    email=email,
                    phone_number=phone_number,
                    first_name=first_name,
                    last_name=last_name,
                )

                print(f"DEBUG: Пользователь {username} успешно создан!")
                messages.success(request, f'Пользователь {username} создан!')
                return redirect('admin:user_management')
            except Exception as e:
                error_msg = f'Ошибка при создании пользователя: {e}'
                messages.error(request, error_msg)
                print(f"DEBUG: {error_msg}")

    return render(request, 'admin/create_user.html')

@login_required
def edit_user(request, user_id):
    if not is_superadmin(request.user):
        messages.error(request, 'Доступ запрещен')
        return redirect('home')

    try:
        user_to_edit = User.objects.get(id=user_id)

        # Не позволяем редактировать системного админа
        if user_to_edit.username == 'systemadmin':
            messages.error(request, 'Нельзя редактировать системного администратора')
            return redirect('admin:user_management')

        if request.method == 'POST':
            # Обновляем данные пользователя
            user_to_edit.email = request.POST.get('email', '')
            user_to_edit.first_name = request.POST.get('first_name', '')
            user_to_edit.last_name = request.POST.get('last_name', '')
            user_to_edit.role = request.POST.get('role', 'recruiter')
            user_to_edit.phone_number = request.POST.get('phone_number', '')

            # Если указан новый пароль
            new_password = request.POST.get('password')
            if new_password:
                user_to_edit.set_password(new_password)

            user_to_edit.save()
            messages.success(request, f'Пользователь {user_to_edit.username} успешно обновлен!')
            return redirect('admin:user_management')

        # Показываем форму редактирования
        return render(request, 'admin/edit_user.html', {'user_obj': user_to_edit})

    except User.DoesNotExist:
        messages.error(request, 'Пользователь не найден')
        return redirect('admin:user_management')


@login_required
def delete_user(request, user_id):
    if not is_superadmin(request.user):
        messages.error(request, 'Доступ запрещен')
        return redirect('home')

    try:
        user_to_delete = User.objects.get(id=user_id)

        # Не позволяем удалить системного админа
        if user_to_delete.username == 'systemadmin':
            messages.error(request, 'Нельзя удалить системного администратора')
            return redirect('admin:user_management')

        if request.method == 'POST':
            username = user_to_delete.username
            user_to_delete.delete()
            messages.success(request, f'Пользователь {username} успешно удален!')
            return redirect('admin:user_management')

        # Показываем страницу подтверждения
        return render(request, 'admin/confirm_delete.html', {'user_obj': user_to_delete})

    except User.DoesNotExist:
        messages.error(request, 'Пользователь не найден')
        return redirect('admin:user_management')