from django.db import models
from django.conf import settings

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название навыка")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

class Vacancy(models.Model):
    STATUS_CHOICES = (
        ('open', 'Открыта'),
        ('closed', 'Закрыта'),
        ('draft', 'Черновик'),
    )

    title = models.CharField(max_length=200, verbose_name="Название вакансии")
    description = models.TextField(verbose_name="Описание")
    required_skills = models.ManyToManyField(Skill, blank=True, verbose_name="Требуемые навыки")
    required_experience = models.PositiveIntegerField(default=0, verbose_name="Требуемый опыт (лет)")
    salary = models.PositiveIntegerField(null=True, blank=True, verbose_name="Зарплата")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"