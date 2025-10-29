import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_agency.settings')
django.setup()

from django.contrib.auth import get_user_model
from vacancies.models import Skill


def setup_project():
    print("🚀 Настройка HR-системы...")

    User = get_user_model()

    # Создаем пользователей
    users_data = [
        {'username': 'admin', 'password': 'admin123', 'role': 'administrator', 'email': 'admin@hr.ru'},
        {'username': 'manager', 'password': 'manager123', 'role': 'manager', 'email': 'manager@hr.ru'},
        {'username': 'recruiter', 'password': 'recruiter123', 'role': 'recruiter', 'email': 'recruiter@hr.ru'},
    ]

    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={'email': user_data['email'], 'role': user_data['role']}
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"✅ Создан пользователь: {user_data['username']} / {user_data['password']}")

    # Создаем навыки
    skills_list = ['Python', 'Django', 'JavaScript', 'React', 'SQL', 'Docker', 'Git']
    for skill_name in skills_list:
        skill, created = Skill.objects.get_or_create(name=skill_name)
        if created:
            print(f"✅ Создан навык: {skill_name}")

    print("\n🎉 Настройка завершена!")
    print("\n🔑 Доступные логины:")
    print("admin / admin123 (Администратор)")
    print("manager / manager123 (Менеджер)")
    print("recruiter / recruiter123 (Рекрутер)")


if __name__ == "__main__":
    setup_project()