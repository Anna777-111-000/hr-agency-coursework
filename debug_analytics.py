import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_agency.settings')
django.setup()

from candidates.models import Candidate, Application, Interview
from vacancies.models import Vacancy


def debug_analytics():
    print("=== DEBUG ANALYTICS ===")

    # Проверяем данные в базе
    print(f"Кандидатов в базе: {Candidate.objects.count()}")
    print(f"Вакансий в базе: {Vacancy.objects.count()}")
    print(f"Заявок в базе: {Application.objects.count()}")
    print(f"Собеседований в базе: {Interview.objects.count()}")

    # Проверяем опыт работы
    experience_stats = {
        'junior': Candidate.objects.filter(experience_years__lt=2).count(),
        'middle': Candidate.objects.filter(experience_years__range=[2, 5]).count(),
        'senior': Candidate.objects.filter(experience_years__gt=5).count(),
    }
    print(f"Статистика опыта: {experience_stats}")

    # Проверяем статусы вакансий
    print(f"Открытых вакансий: {Vacancy.objects.filter(status='open').count()}")
    print(f"Закрытых вакансий: {Vacancy.objects.filter(status='closed').count()}")


if __name__ == "__main__":
    debug_analytics()