from django.db import models
from django.conf import settings
from vacancies.models import Skill


class Candidate(models.Model):
    # Основная информация
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    patronymic = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="Возраст")
    experience_years = models.PositiveIntegerField(default=0, verbose_name="Опыт работы (лет)")

    # Профессиональная информация
    specialization = models.CharField(max_length=200, blank=True, verbose_name="Специализация")
    position_level = models.CharField(max_length=20, choices=[
        ('intern', 'Intern'),
        ('junior', 'Junior'),
        ('middle', 'Middle'),
        ('senior', 'Senior'),
        ('lead', 'Lead')
    ], blank=True, verbose_name="Уровень позиции")

    # Статус и формат работы
    employment_status = models.CharField(max_length=20, choices=[
        ('employed', 'Трудоустроен'),
        ('unemployed', 'В поиске'),
        ('part_time', 'Частичная занятость'),
        ('student', 'Студент')
    ], default='unemployed', verbose_name="Статус трудоустройства")

    work_format = models.CharField(max_length=20, choices=[
        ('office', 'Офис'),
        ('remote', 'Удаленно'),
        ('hybrid', 'Гибрид')
    ], blank=True, verbose_name="Формат работы")

    # История работы
    last_workplace = models.CharField(max_length=200, blank=True, verbose_name="Последнее место работы")
    last_position = models.CharField(max_length=200, blank=True, verbose_name="Должность")
    work_period = models.CharField(max_length=100, blank=True, verbose_name="Период работы")
    responsibilities = models.TextField(blank=True, verbose_name="Обязанности и достижения")

    # Образование
    education_level = models.CharField(max_length=50, choices=[
        ('secondary', 'Среднее'),
        ('specialized_secondary', 'Среднее специальное'),
        ('incomplete_higher', 'Неполное высшее'),
        ('higher', 'Высшее'),
        ('bachelor', 'Бакалавр'),
        ('master', 'Магистр'),
        ('phd', 'Кандидат наук'),
        ('doctor', 'Доктор наук'),
    ], blank=True, verbose_name="Уровень образования")
    education_institution = models.CharField(max_length=200, blank=True, verbose_name="ВУЗ/Курсы")
    education_specialty = models.CharField(max_length=200, blank=True, verbose_name="Специальность")
    graduation_year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Год окончания")

    # Навыки
    skills = models.ManyToManyField('vacancies.Skill', blank=True, verbose_name="Навыки")

    # Источник и рекрутер
    source = models.CharField(max_length=100, choices=[
        ('hh', 'HH.ru'),
        ('linkedin', 'LinkedIn'),
        ('habr', 'Habr Career'),
        ('recommendation', 'Рекомендация'),
        ('other', 'Другое')
    ], default='hh', verbose_name="Источник кандидата")
    source_details = models.CharField(max_length=200, blank=True, verbose_name="Детали источника")
    assigned_recruiter = models.CharField(max_length=100, blank=True, verbose_name="Ответственный рекрутер")

    # Файлы
    resume = models.FileField(
        upload_to='resumes/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Резюме (файл)"
    )

    # Примечания
    recruiter_notes = models.TextField(blank=True, verbose_name="Примечания рекрутера")
    next_actions = models.TextField(blank=True, verbose_name="План следующих действий")
    candidate_features = models.TextField(blank=True, verbose_name="Особенности кандидата")

    # Зарплата и выход
    desired_salary = models.PositiveIntegerField(null=True, blank=True, verbose_name="Желаемая зарплата")
    notice_period = models.CharField(max_length=50, blank=True, verbose_name="Срок выхода на работу")

    # Временные метки
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
    notes = models.TextField(blank=True, verbose_name="Комментарий рекрутера")

    class Meta:
        unique_together = ['candidate', 'vacancy']
        verbose_name = "Отклик"
        verbose_name_plural = "Отклики"

    def __str__(self):
        return f"{self.candidate} -> {self.vacancy} ({self.status})"


class Interview(models.Model):
    INTERVIEW_TYPE_CHOICES = (
        ('phone', '📞 Телефонное'),
        ('video', '🎥 Видео-собеседование'),
        ('in_person', '👥 Личная встреча'),
        ('technical', '💻 Техническое'),
        ('hr', '👔 HR-собеседование'),
    )

    STATUS_CHOICES = (
        ('scheduled', 'Запланировано'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
        ('no_show', 'Кандидат не явился'),
    )

    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE, related_name='interviews')
    scheduled_date = models.DateTimeField(verbose_name="Дата и время собеседования")
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPE_CHOICES, verbose_name="Тип собеседования")
    notes = models.TextField(blank=True, verbose_name="Заметки")
    scheduled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Запланировал")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Статус")
    feedback = models.TextField(blank=True, verbose_name="Отзыв после собеседования")
    result = models.CharField(max_length=20, choices=[('positive', 'Положительный'), ('negative', 'Отрицательный'),
                                                      ('neutral', 'Нейтральный')], blank=True, verbose_name="Результат")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    reminder_sent = models.BooleanField(default=False, verbose_name="Напоминание отправлено")
    reminder_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата напоминания")

    def __str__(self):
        return f"Собеседование {self.candidate} - {self.scheduled_date.strftime('%d.%m.%Y %H:%M')}"

    class Meta:
        verbose_name = "Собеседование"
        verbose_name_plural = "Собеседования"
        ordering = ['-scheduled_date']


# форма кандидатов
class PersonnelForm(models.Model):
    # Форма для отдела кадров предприятия

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

    skills = models.ManyToManyField('vacancies.Skill', blank=True, verbose_name="Навыки")
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