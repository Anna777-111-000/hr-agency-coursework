# HR Agency - Автоматизированное рабочее место работника кадрового агентства

Веб-приложение для автоматизации работы кадрового агентства.

## Функционал
- Управление кандидатами и вакансиями
- Система ролей (Рекрутер, Менеджер, Администратор)
- Фильтрация и поиск кандидатов
- Система откликов и рейтинга

## Технологии
- Python 3.8+
- Django 5.2
- Bootstrap 5
- SQLite
- 
# Установка

1. Клонировать репозиторий  
2. Создать виртуальное окружение: python -m venv venv  
3. Активировать окружение: source venv/bin/activate / venv\Scripts\activate  
4. Установить зависимости: pip install -r requirements.txt  
5. Если зависимости не установились, выполнить: pip install django django-crispy-forms pillow crispy-bootstrap5  
6. Выполнить миграции: python manage.py migrate  
7. Создать тестовых пользователей: python setup.py  
8. Запустить сервер: python manage.py runserver  

# Тестовые пользователи

- Администратор: admin / admin123
- Менеджер: manager / manager123  
- Рекрутер: recruiter / recruiter123
