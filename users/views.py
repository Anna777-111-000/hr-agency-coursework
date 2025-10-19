from django.shortcuts import render, redirect


def home(request):
    # Если пользователь - суперадмин, перенаправляем в админ-панель
    if request.user.is_authenticated and request.user.username == 'systemadmin':
        return redirect('admin:superadmin_dashboard')

    # Остальная логика главной страницы
    return render(request, 'home.html')