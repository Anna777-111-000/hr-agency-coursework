from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('recruiter', 'Рекрутер'),
        ('manager', 'Менеджер'),
        ('administrator', 'Администратор'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='recruiter')
    phone_number = models.CharField(max_length=20)

    def get_role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)

    def delete(self, *args, **kwargs):
        # Защита от удаления системного администратора
        if self.username == 'systemadmin':
            raise PermissionError("Нельзя удалить системного администратора")
        super().delete(*args, **kwargs)

    def is_system_admin(self):
        """Проверяет, является ли пользователь системным администратором"""
        return self.username == 'systemadmin'