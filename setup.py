import os
import django
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_agency.settings')
django.setup()

from django.contrib.auth import get_user_model
from vacancies.models import Skill, Vacancy
from candidates.models import Candidate, PersonnelForm
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
            'phone_number': '+79991112233',
            'is_staff': True,
            'is_superuser': True
        },
        {
            'username': 'manager',
            'password': 'manager123',
            'role': 'manager',
            'email': 'manager@hr.ru',
            'phone_number': '+79992223344',
            'is_staff': True,
            'is_superuser': False
        },
        {
            'username': 'recruiter',
            'password': 'recruiter123',
            'role': 'recruiter',
            'email': 'recruiter@hr.ru',
            'phone_number': '+79993334455',
            'is_staff': False,
            'is_superuser': False
        },
        {
            'username': 'recruiter2',
            'password': 'recruiter123',
            'role': 'recruiter',
            'email': 'recruiter2@hr.ru',
            'phone_number': '+79994445566',
            'is_staff': False,
            'is_superuser': False
        },
    ]
    print(" Обновление прав доступа пользователей...")
    for user in User.objects.all():
        if user.role == 'admin':
            user.is_staff = True
            user.is_superuser = True
        elif user.role == 'manager':
            user.is_staff = True
            user.is_superuser = False
        else:
            user.is_staff = False
            user.is_superuser = False
        user.save()

    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'role': user_data['role'],
                'phone_number': user_data['phone_number'],
                'is_staff': user_data['is_staff'],
                'is_superuser': user_data['is_superuser']
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f" Создан пользователь: {user_data['username']} / {user_data['password']}")
        else:
            user.email = user_data['email']
            user.role = user_data['role']
            user.phone_number = user_data['phone_number']
            user.is_staff = user_data['is_staff']
            user.is_superuser = user_data['is_superuser']
            user.set_password(user_data['password'])
            user.save()
            print(f" Обновлен пользователь: {user_data['username']}")

    # Создаем навыки
    skills_list = [
        'Python', 'Django', 'JavaScript', 'React', 'Vue.js', 'Angular',
        'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Docker', 'Kubernetes',
        'Git', 'HTML/CSS', 'Linux', 'AWS', 'Redis', 'Celery', 'REST API',
        'GraphQL', 'TypeScript', 'Node.js', 'FastAPI', 'Flask', 'Pandas',
        'NumPy', 'Machine Learning', 'Data Analysis', 'UI/UX Design',
        'Project Management', 'Agile/Scrum', 'Testing', 'CI/CD'
    ]

    skills_objects = []
    for skill_name in skills_list:
        skill, created = Skill.objects.get_or_create(name=skill_name)
        if created:
            print(f" Создан навык: {skill_name}")
        skills_objects.append(skill)

    # Создаем вакансии
    vacancies_data = [
        {
            'title': 'Python разработчик',
            'description': 'Разработка backend-части веб-приложений на Python и Django. Требуется опыт работы с базами данных и REST API.',
            'required_experience': 2,
            'salary': 120000,
            'work_format': 'hybrid',
            'status': 'open',
            'location': 'Москва',
            'employment_type': 'full_time'
        },
        {
            'title': 'Frontend разработчик (React)',
            'description': 'Разработка пользовательских интерфейсов на React. Знание TypeScript будет плюсом.',
            'required_experience': 1,
            'salary': 100000,
            'work_format': 'remote',
            'status': 'open',
            'location': 'Удаленно',
            'employment_type': 'full_time'
        },
        {
            'title': 'Fullstack разработчик',
            'description': 'Разработка полного стека приложений. Python/Django + React. Опыт работы с Docker.',
            'required_experience': 3,
            'salary': 150000,
            'work_format': 'office',
            'status': 'open',
            'location': 'Санкт-Петербург',
            'employment_type': 'full_time'
        },
        {
            'title': 'DevOps инженер',
            'description': 'Настройка инфраструктуры и CI/CD процессов. Опыт с AWS, Docker, Kubernetes.',
            'required_experience': 2,
            'salary': 140000,
            'work_format': 'hybrid',
            'status': 'draft',
            'location': 'Москва',
            'employment_type': 'full_time'
        },
        {
            'title': 'Data Analyst',
            'description': 'Анализ данных и построение отчетов. Знание SQL, Python, инструментов визуализации.',
            'required_experience': 1,
            'salary': 90000,
            'work_format': 'remote',
            'status': 'closed',
            'location': 'Удаленно',
            'employment_type': 'full_time'
        },
        {
            'title': 'Senior Python Developer',
            'description': 'Разработка высоконагруженных систем. Архитектура, оптимизация, менторинг.',
            'required_experience': 5,
            'salary': 200000,
            'work_format': 'hybrid',
            'status': 'open',
            'location': 'Москва',
            'employment_type': 'full_time'
        }
    ]

    manager_user = User.objects.get(username='manager')
    recruiter_user = User.objects.get(username='recruiter')

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
                'employment_type': vacancy_data['employment_type'],
                'created_by': manager_user,
                'assigned_recruiter': recruiter_user
            }
        )

        if created:
            # Добавляем релевантные навыки к вакансии
            relevant_skills = []
            title_lower = vacancy_data['title'].lower()

            if 'python' in title_lower:
                relevant_skills.extend(['Python', 'Django', 'Flask', 'FastAPI', 'SQL'])
            if 'frontend' in title_lower or 'react' in title_lower:
                relevant_skills.extend(['JavaScript', 'React', 'HTML/CSS', 'TypeScript'])
            if 'fullstack' in title_lower:
                relevant_skills.extend(['Python', 'Django', 'React', 'JavaScript', 'SQL'])
            if 'devops' in title_lower:
                relevant_skills.extend(['Docker', 'Kubernetes', 'AWS', 'Linux', 'CI/CD'])
            if 'data' in title_lower:
                relevant_skills.extend(['SQL', 'Python', 'Pandas', 'Data Analysis'])

            # Убираем дубликаты и добавляем случайные навыки
            relevant_skills = list(set(relevant_skills))
            if len(relevant_skills) < 3:
                relevant_skills.extend(random.sample([s.name for s in skills_objects], 3 - len(relevant_skills)))

            skills_to_add = [s for s in skills_objects if s.name in relevant_skills]
            vacancy.required_skills.set(skills_to_add)

            print(f" Создана вакансия: {vacancy_data['title']}")
            print(f"   Статус: {vacancy_data['status']}, Зарплата: {vacancy_data['salary']} руб.")

    # Создаем тестовых кандидатов
    candidates_data = [
        {
            'first_name': 'Иван',
            'last_name': 'Петров',
            'patronymic': 'Сергеевич',
            'email': 'ivan.petrov@example.com',
            'phone': '+79991111111',
            'age': 28,
            'experience_years': 3,
            'specialization': 'Python разработчик',
            'position_level': 'middle',
            'employment_status': 'unemployed',
            'work_format': 'hybrid',
            'education_level': 'higher',
            'source': 'hh',
            'assigned_recruiter': 'recruiter',
            'desired_salary': 130000
        },
        {
            'first_name': 'Мария',
            'last_name': 'Сидорова',
            'patronymic': 'Александровна',
            'email': 'maria.sidorova@example.com',
            'phone': '+79992222222',
            'age': 24,
            'experience_years': 1,
            'specialization': 'Frontend разработчик',
            'position_level': 'junior',
            'employment_status': 'employed',
            'work_format': 'remote',
            'education_level': 'bachelor',
            'source': 'linkedin',
            'assigned_recruiter': 'recruiter',
            'desired_salary': 90000
        },
        {
            'first_name': 'Алексей',
            'last_name': 'Козлов',
            'patronymic': 'Дмитриевич',
            'email': 'alexey.kozlov@example.com',
            'phone': '+79993333333',
            'age': 32,
            'experience_years': 5,
            'specialization': 'Fullstack разработчик',
            'position_level': 'senior',
            'employment_status': 'unemployed',
            'work_format': 'office',
            'education_level': 'master',
            'source': 'habr',
            'assigned_recruiter': 'recruiter2',
            'desired_salary': 180000
        },
        {
            'first_name': 'Елена',
            'last_name': 'Николаева',
            'patronymic': 'Владимировна',
            'email': 'elena.nikolaeva@example.com',
            'phone': '+79994444444',
            'age': 26,
            'experience_years': 2,
            'specialization': 'Data Analyst',
            'position_level': 'middle',
            'employment_status': 'part_time',
            'work_format': 'remote',
            'education_level': 'higher',
            'source': 'hh',
            'assigned_recruiter': 'recruiter',
            'desired_salary': 110000
        },
        {
            'first_name': 'Дмитрий',
            'last_name': 'Васильев',
            'patronymic': 'Игоревич',
            'email': 'dmitry.vasiliev@example.com',
            'phone': '+79995555555',
            'age': 35,
            'experience_years': 4,
            'specialization': 'DevOps инженер',
            'position_level': 'senior',
            'employment_status': 'employed',
            'work_format': 'hybrid',
            'education_level': 'higher',
            'source': 'recommendation',
            'assigned_recruiter': 'recruiter2',
            'desired_salary': 160000
        },
        {
            'first_name': 'Анна',
            'last_name': 'Кузнецова',
            'patronymic': 'Сергеевна',
            'email': 'anna.kuznetsova@example.com',
            'phone': '+79996666666',
            'age': 22,
            'experience_years': 0,
            'specialization': 'Frontend разработчик',
            'position_level': 'intern',
            'employment_status': 'student',
            'work_format': 'office',
            'education_level': 'incomplete_higher',
            'source': 'other',
            'assigned_recruiter': 'recruiter',
            'desired_salary': 60000
        }
    ]

    for candidate_data in candidates_data:
        candidate, created = Candidate.objects.get_or_create(
            email=candidate_data['email'],
            defaults=candidate_data
        )

        if created:
            # Добавляем релевантные навыки кандидату
            relevant_skills = []
            specialization_lower = candidate_data['specialization'].lower()

            if 'python' in specialization_lower:
                relevant_skills.extend(['Python', 'Django', 'SQL', 'Git'])
            if 'frontend' in specialization_lower:
                relevant_skills.extend(['JavaScript', 'React', 'HTML/CSS', 'Git'])
            if 'fullstack' in specialization_lower:
                relevant_skills.extend(['Python', 'Django', 'React', 'JavaScript', 'SQL'])
            if 'devops' in specialization_lower:
                relevant_skills.extend(['Docker', 'Linux', 'AWS', 'Git', 'CI/CD'])
            if 'data' in specialization_lower:
                relevant_skills.extend(['SQL', 'Python', 'Pandas', 'Data Analysis'])

            # Добавляем несколько случайных дополнительных навыков
            relevant_skills.extend(random.sample([s.name for s in skills_objects], 2))
            relevant_skills = list(set(relevant_skills))

            skills_to_add = [s for s in skills_objects if s.name in relevant_skills]
            candidate.skills.set(skills_to_add)

            print(f" Создан кандидат: {candidate_data['first_name']} {candidate_data['last_name']}")

    # Создаем тестовые анкеты сотрудников
    personnel_forms_data = [
        {
            'last_name': 'Смирнов',
            'first_name': 'Андрей',
            'patronymic': 'Викторович',
            'birth_date': '1990-05-15',
            'birth_place': 'г. Москва',
            'citizenship': 'Российская Федерация',
            'address': 'г. Москва, ул. Ленина, д. 10, кв. 25',
            'phone': '+79997777777',
            'email': 'andrey.smirnov@company.ru',
            'education': 'higher',
            'institution': 'МГТУ им. Баумана',
            'specialty': 'Информационные системы и технологии',
            'graduation_year': 2012,
            'marital_status': 'married',
            'passport_series': '4510',
            'passport_number': '123456',
            'passport_issued_by': 'ОУФМС России по г. Москве',
            'passport_issue_date': '2010-05-20',
            'passport_department_code': '770-001',
            'inn': '123456789012',
            'snils': '123-456-789-00',
            'military_duty': True,
            'military_rank': 'лейтенант',
            'military_specialty': 'программист',
            'work_experience_total': 10,
            'work_experience_specialty': 8,
            'is_approved': True
        },
        {
            'last_name': 'Орлова',
            'first_name': 'Татьяна',
            'patronymic': 'Михайловна',
            'birth_date': '1988-08-22',
            'birth_place': 'г. Санкт-Петербург',
            'citizenship': 'Российская Федерация',
            'address': 'г. Санкт-Петербург, Невский пр-т, д. 50, кв. 12',
            'phone': '+79998888888',
            'email': 'tatiana.orlova@company.ru',
            'education': 'master',
            'institution': 'СПбГУ',
            'specialty': 'Прикладная математика и информатика',
            'graduation_year': 2010,
            'marital_status': 'single',
            'passport_series': '4012',
            'passport_number': '654321',
            'passport_issued_by': 'ОУФМС России по г. Санкт-Петербургу',
            'passport_issue_date': '2008-08-15',
            'passport_department_code': '780-002',
            'inn': '987654321098',
            'snils': '987-654-321-00',
            'military_duty': False,
            'military_rank': '',
            'military_specialty': '',
            'work_experience_total': 12,
            'work_experience_specialty': 10,
            'is_approved': True
        },
        {
            'last_name': 'Волков',
            'first_name': 'Сергей',
            'patronymic': 'Анатольевич',
            'birth_date': '1995-12-03',
            'birth_place': 'г. Екатеринбург',
            'citizenship': 'Российская Федерация',
            'address': 'г. Екатеринбург, ул. Мира, д. 15, кв. 8',
            'phone': '+79999999999',
            'email': 'sergey.volkov@company.ru',
            'education': 'bachelor',
            'institution': 'УрФУ',
            'specialty': 'Программная инженерия',
            'graduation_year': 2017,
            'marital_status': 'married',
            'passport_series': '5001',
            'passport_number': '111222',
            'passport_issued_by': 'ОУФМС России по Свердловской области',
            'passport_issue_date': '2013-12-10',
            'passport_department_code': '660-003',
            'inn': '111222333444',
            'snils': '111-222-333-44',
            'military_duty': True,
            'military_rank': 'рядовой',
            'military_specialty': 'связист',
            'work_experience_total': 5,
            'work_experience_specialty': 4,
            'is_approved': False
        }
    ]

    for form_data in personnel_forms_data:
        form, created = PersonnelForm.objects.get_or_create(
            email=form_data['email'],
            defaults=form_data
        )

        if created:
            # Добавляем навыки к анкете
            skills_to_add = random.sample(skills_objects, min(5, len(skills_objects)))
            form.skills.set(skills_to_add)

            print(f" Создана анкета сотрудника: {form_data['last_name']} {form_data['first_name']}")

    print("\n Настройка завершена!")
    print("\n Доступные логины:")
    print("admin / admin123 (Администратор) - полный доступ")
    print("manager / manager123 (Менеджер) - доступ к админке")
    print("recruiter / recruiter123 (Рекрутер) - обычный пользователь")
    print("recruiter2 / recruiter123 (Рекрутер 2) - обычный пользователь")

    print(f"\n Создано:")
    print(f"    Пользователей: {User.objects.count()}")
    print(f"    Вакансий: {Vacancy.objects.count()}")
    print(f"    Кандидатов: {Candidate.objects.count()}")
    print(f"    Анкет сотрудников: {PersonnelForm.objects.count()}")
    print(f"    Навыков: {Skill.objects.count()}")


if __name__ == "__main__":
    setup_project()