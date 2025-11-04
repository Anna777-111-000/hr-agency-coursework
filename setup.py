import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_agency.settings')
django.setup()

from django.contrib.auth import get_user_model
from vacancies.models import Skill, Vacancy
from candidates.models import Candidate
import random
from datetime import datetime, timedelta


def setup_project():
    print("🚀 Настройка HR-системы...")

    User = get_user_model()

    # Создаем пользователей с правами доступа к админке
    users_data = [
        {
            'username': 'admin',
            'password': 'admin123',
            'role': 'admin',
            'email': 'admin@hr.ru',
            'is_staff': True,  # Может заходить в админку
            'is_superuser': True  # Полные права в админке
        },
        {
            'username': 'manager',
            'password': 'manager123',
            'role': 'manager',
            'email': 'manager@hr.ru',
            'is_staff': True,  # Может заходить в админку
            'is_superuser': False  # Ограниченные права
        },
        {
            'username': 'recruiter',
            'password': 'recruiter123',
            'role': 'recruiter',
            'email': 'recruiter@hr.ru',
            'is_staff': False,  # Не может заходить в админку
            'is_superuser': False  # Обычный пользователь
        },
    ]

    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'role': user_data['role'],
                'is_staff': user_data['is_staff'],
                'is_superuser': user_data['is_superuser']
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"✅ Создан пользователь: {user_data['username']} / {user_data['password']}")
            print(
                f"   Роль: {user_data['role']}, Staff: {user_data['is_staff']}, Superuser: {user_data['is_superuser']}")
        else:
            # Обновляем существующего пользователя
            user.email = user_data['email']
            user.role = user_data['role']
            user.is_staff = user_data['is_staff']
            user.is_superuser = user_data['is_superuser']
            user.set_password(user_data['password'])
            user.save()
            print(f"✅ Обновлен пользователь: {user_data['username']}")
            print(
                f"   Роль: {user_data['role']}, Staff: {user_data['is_staff']}, Superuser: {user_data['is_superuser']}")

    # Создаем навыки
    skills_list = ['Python', 'Django', 'JavaScript', 'React', 'SQL', 'Docker', 'Git', 'HTML/CSS', 'PostgreSQL', 'Linux']
    skills_objects = []
    for skill_name in skills_list:
        skill, created = Skill.objects.get_or_create(name=skill_name)
        if created:
            print(f"✅ Создан навык: {skill_name}")
        skills_objects.append(skill)

    # Создаем вакансии
    vacancies_data = [
        {
            'title': 'Python разработчик',
            'description': 'Разработка backend-части веб-приложений на Python и Django',
            'required_experience': 2,
            'salary': 120000,
            'work_format': 'hybrid',
            'status': 'open',
            'location': 'Москва'
        },
        {
            'title': 'Frontend разработчик',
            'description': 'Разработка пользовательских интерфейсов на React',
            'required_experience': 1,
            'salary': 100000,
            'work_format': 'remote',
            'status': 'open',
            'location': 'Удаленно'
        },
        {
            'title': 'Fullstack разработчик',
            'description': 'Разработка полного стека приложений',
            'required_experience': 3,
            'salary': 150000,
            'work_format': 'office',
            'status': 'open',
            'location': 'Санкт-Петербург'
        },
        {
            'title': 'DevOps инженер',
            'description': 'Настройка инфраструктуры и CI/CD процессов',
            'required_experience': 2,
            'salary': 140000,
            'work_format': 'hybrid',
            'status': 'draft',
            'location': 'Москва'
        },
        {
            'title': 'Data Analyst',
            'description': 'Анализ данных и построение отчетов',
            'required_experience': 1,
            'salary': 90000,
            'work_format': 'remote',
            'status': 'closed',
            'location': 'Удаленно'
        }
    ]

    manager_user = User.objects.get(username='manager')

    for vacancy_data in vacancies_data:
        vacancy, created = Vacancy.objects.get_or_create(
            title=vacancy_data['title'],
            defaults={
                'description': vacancy_data['description'],
                'required_experience': vacancy_data['required_experience'],
                'salary': vacancy_data['salary'],
                'work_format': vacancy_data['work_format'],
                'status': vacancy_data['status'],
                'location': vacancy_data['location'],
                'created_by': manager_user,
                'employment_type': 'full_time'
            }
        )

        if created:
            # Добавляем случайные навыки к вакансии
            random_skills = random.sample(skills_objects, min(3, len(skills_objects)))
            vacancy.required_skills.set(random_skills)
            print(f"✅ Создана вакансия: {vacancy_data['title']}")
            print(f"   Статус: {vacancy_data['status']}, Зарплата: {vacancy_data['salary']} руб.")

    # Создаем тестовых кандидатов
    candidates_data = [
        {
            'first_name': 'Иван',
            'last_name': 'Петров',
            'email': 'ivan.petrov@example.com',
            'experience_years': 3,
            'specialization': 'Python разработчик',
            'position_level': 'middle'
        },
        {
            'first_name': 'Мария',
            'last_name': 'Сидорова',
            'email': 'maria.sidorova@example.com',
            'experience_years': 1,
            'specialization': 'Frontend разработчик',
            'position_level': 'junior'
        },
        {
            'first_name': 'Алексей',
            'last_name': 'Козлов',
            'email': 'alexey.kozlov@example.com',
            'experience_years': 5,
            'specialization': 'Fullstack разработчик',
            'position_level': 'senior'
        },
        {
            'first_name': 'Елена',
            'last_name': 'Николаева',
            'email': 'elena.nikolaeva@example.com',
            'experience_years': 2,
            'specialization': 'Data Analyst',
            'position_level': 'middle'
        },
        {
            'first_name': 'Дмитрий',
            'last_name': 'Васильев',
            'email': 'dmitry.vasiliev@example.com',
            'experience_years': 4,
            'specialization': 'DevOps инженер',
            'position_level': 'senior'
        }
    ]

    for candidate_data in candidates_data:
        candidate, created = Candidate.objects.get_or_create(
            email=candidate_data['email'],
            defaults={
                'first_name': candidate_data['first_name'],
                'last_name': candidate_data['last_name'],
                'experience_years': candidate_data['experience_years'],
                'specialization': candidate_data['specialization'],
                'position_level': candidate_data['position_level'],
                'employment_status': 'unemployed',
                'work_format': random.choice(['office', 'remote', 'hybrid']),
                'education_level': 'higher',
                'source': random.choice(['hh', 'linkedin', 'habr']),
                'assigned_recruiter': 'recruiter'
            }
        )

        if created:
            # Добавляем случайные навыки кандидату
            random_skills = random.sample(skills_objects, min(4, len(skills_objects)))
            candidate.skills.set(random_skills)
            print(f"✅ Создан кандидат: {candidate_data['first_name']} {candidate_data['last_name']}")

    print("\n🎉 Настройка завершена!")
    print("\n🔑 Доступные логины:")
    print("admin / admin123 (Администратор) - полный доступ к админке")
    print("manager / manager123 (Менеджер) - ограниченный доступ к админке")
    print("recruiter / recruiter123 (Рекрутер) - без доступа к админке")
    print(f"\n📊 Создано: {Vacancy.objects.count()} вакансий, {Candidate.objects.count()} кандидатов")


if __name__ == "__main__":
    setup_project()