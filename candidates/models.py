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
    resume = models.FileField(upload_to='resumes/', blank=True, null=True, verbose_name="Резюме (файл)")
    skills = models.ManyToManyField('vacancies.Skill', blank=True, verbose_name="Навыки")
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

    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE, related_name='applications',
                                  verbose_name="Кандидат")
    vacancy = models.ForeignKey('vacancies.Vacancy', on_delete=models.CASCADE, related_name='applications',
                                verbose_name="Вакансия")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус заявки")
    applied_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата отклика")

    class Meta:
        unique_together = ['candidate', 'vacancy']
        verbose_name = "Отклик"
        verbose_name_plural = "Отклики"

    def __str__(self):
        return f"{self.candidate} -> {self.vacancy} ({self.status})"


# НОВАЯ МОДЕЛЬ ДЛЯ ФОРМЫ КАДРОВ - ДОБАВЛЯЕМ В КОНЕЦ ФАЙЛА
class PersonnelForm(models.Model):
    """Форма для отдела кадров предприятия"""

    EDUCATION_CHOICES = (
        ('secondary', 'Среднее'),
        ('specialized_secondary', 'Среднее специальное'),
        ('incomplete_higher', 'Неполное высшее'),
        ('higher', 'Высшее'),
        ('bachelor', 'Бакалавр'),
        ('master', 'Магистр'),
        ('phd', 'Кандидат наук'),
        ('doctor', 'Доктор наук'),
    )

    MARITAL_STATUS_CHOICES = (
        ('single', 'Холост/Не замужем'),
        ('married', 'Женат/Замужем'),
        ('divorced', 'Разведен(а)'),
        ('widowed', 'Вдовец/Вдова'),
    )

    # Основная информация
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    patronymic = models.CharField(max_length=100, verbose_name="Отчество")
    birth_date = models.DateField(verbose_name="Дата рождения")
    birth_place = models.CharField(max_length=200, verbose_name="Место рождения")
    citizenship = models.CharField(max_length=100, verbose_name="Гражданство", default="Российская Федерация")

    # Контактная информация
    address = models.TextField(verbose_name="Адрес проживания")
    phone = models.CharField(max_length=20, verbose_name="Контактный телефон")
    email = models.EmailField(verbose_name="Электронная почта")

    # Образование
    education = models.CharField(max_length=50, choices=EDUCATION_CHOICES, verbose_name="Образование")
    institution = models.CharField(max_length=200, verbose_name="Учебное заведение")
    specialty = models.CharField(max_length=200, verbose_name="Специальность по диплому")
    graduation_year = models.PositiveIntegerField(verbose_name="Год окончания")

    # Семейное положение
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, verbose_name="Семейное положение")

    # Паспортные данные
    passport_series = models.CharField(max_length=4, verbose_name="Серия паспорта")
    passport_number = models.CharField(max_length=6, verbose_name="Номер паспорта")
    passport_issued_by = models.TextField(verbose_name="Кем выдан")
    passport_issue_date = models.DateField(verbose_name="Дата выдачи")
    passport_department_code = models.CharField(max_length=7, verbose_name="Код подразделения")

    # ИНН и СНИЛС
    inn = models.CharField(max_length=12, verbose_name="ИНН", blank=True)
    snils = models.CharField(max_length=14, verbose_name="СНИЛС", blank=True)

    # Воинский учет
    military_duty = models.BooleanField(default=False, verbose_name="Военнообязанный")
    military_rank = models.CharField(max_length=50, blank=True, verbose_name="Воинское звание")
    military_specialty = models.CharField(max_length=100, blank=True, verbose_name="Военно-учетная специальность")

    # Трудовая деятельность
    work_experience_total = models.PositiveIntegerField(verbose_name="Общий стаж работы (лет)")
    work_experience_specialty = models.PositiveIntegerField(verbose_name="Стаж работы по специальности (лет)")

    # Дополнительная информация
    additional_info = models.TextField(blank=True, verbose_name="Дополнительная информация")

    # Служебные поля
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_approved = models.BooleanField(default=False, verbose_name="Проверено отделом кадров")

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}"

    class Meta:
        verbose_name = "Анкета сотрудника"
        verbose_name_plural = "Анкеты сотрудников"
        ordering = ['-created_at']