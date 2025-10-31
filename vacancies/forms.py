from django import forms
from .models import Vacancy


class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = [
            'title', 'description', 'required_skills', 'required_experience',
            'salary', 'work_format', 'status', 'assigned_recruiter',
            'location', 'employment_type'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Python разработчик'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Подробное описание вакансии, требования, условия работы...'
            }),
            'required_skills': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '8'
            }),
            'required_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '50'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Укажите зарплату'
            }),
            'work_format': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'assigned_recruiter': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Город или удаленно'
            }),
            'employment_type': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'assigned_recruiter': 'Назначить рекрутера',
            'work_format': 'Формат работы',
            'employment_type': 'Тип занятости',
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Ограничиваем выбор рекрутеров только пользователями с ролью recruiter
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields['assigned_recruiter'].queryset = User.objects.filter(role='recruiter')

        # Для новых вакансий устанавливаем создателя
        if not self.instance.pk and self.request:
            self.instance.created_by = self.request.user

    def clean_salary(self):
        salary = self.cleaned_data.get('salary')
        if salary and salary < 0:
            raise forms.ValidationError("Зарплата не может быть отрицательной")
        return salary

    def clean_required_experience(self):
        experience = self.cleaned_data.get('required_experience')
        if experience and experience > 50:
            raise forms.ValidationError("Опыт работы не может превышать 50 лет")
        return experience