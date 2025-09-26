from tabnanny import verbose

from django.db import models
from django.conf import settings

# Создаем модель наавыки
class Skill(models.Model): # Это сообщает, что данный класс является моделью, и для него нужно создать таблицу в БД
    name = models.CharField(max_length=100, unique=True, verbose_name="Название навыка") #MAX_dlina, ограниечение уникальности, в человеческий формат

# Метод, определяет, как объект будет отображаться в интерфейсе
    def __str__(self): # ввыведет в виде текста
        return self.name

# Класс для дополнительных настроек модели
    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

# Cписок возможных значений для поля status
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

  # автоматически устанавливает текущую дату при создании
    created_at = models.DateTimeField(auto_now_add=True)
  # автоматически обновляет дату при каждом изменении
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
      return self.title


    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"