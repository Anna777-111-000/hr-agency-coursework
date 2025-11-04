from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('recruiter', 'Рекрутер'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='recruiter')
    phone_number = models.CharField(max_length=20, blank=True)

    def get_role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)

    def is_manager(self):
        return self.role in ['manager', 'admin']

    def is_admin(self):
        return self.role == 'admin'

    def is_recruiter(self):
        return self.role == 'recruiter'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"