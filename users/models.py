from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('recruiter', 'Рекрутер'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='recruiter')
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def delete(self, *args, **kwargs):
        """Защита от удаления системного пользователя"""
        if self.is_system_user:
            raise ValueError("Нельзя удалить системного пользователя")
        super().delete(*args, **kwargs)