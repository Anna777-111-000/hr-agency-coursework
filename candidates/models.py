from django.db import models
from vacancies.models import Skill

class Candidate(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    patronymic = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=15, blank=True, verbose_name="Телефон")


    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="Возраст")
    experience_years = models.PositiveIntegerField(default=0, verbose_name="Опыт работы (лет)")
    resume = models.FileField(upload_to='resumes/', blank=True, null=True, verbose_name="Резюме (файл)") # Поле для загрузки файлов
    skills = models.ManyToManyField(Skill, blank=True, verbose_name="Навыки")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.patronymic}".strip()


    class Meta:
        verbose_name = "Кандидат"
        verbose_name_plural = "Кандидаты"


class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрен'),
        ('rejected', 'Отклонен'),
    )
# Связь между кандидатами, отдельная таблица
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications', verbose_name="Кандидат")
    vacancy = models.ForeignKey('vacancies.Vacancy', on_delete=models.CASCADE, related_name='applications', verbose_name="Вакансия")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус заявки")
    applied_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата отклика")

    class Meta:
        unique_together = ['candidate', 'vacancy']
        verbose_name = "Отклик"
        verbose_name_plural = "Отклики"

    def __str__(self):
        return f"{self.candidate} -> {self.vacancy} ({self.status})"

