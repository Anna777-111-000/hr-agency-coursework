from django.shortcuts import render, redirect


def home(request):
    context = {
        'user': request.user
    }
    return render(request, 'home.html', context)

    # Остальная логика главной страницы
    return render(request, 'home.html')