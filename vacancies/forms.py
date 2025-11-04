from django import forms
from .models import Vacancy, Skill

class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = [
            'title', 'description', 'required_skills', 'required_experience',
            'salary', 'work_format', 'status', 'location', 'employment_type'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название вакансии'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Опишите вакансию',
                'rows': 4
            }),
            'required_skills': forms.SelectMultiple(attrs={
                'class': 'form-control'
            }),
            'required_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Лет опыта'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Зарплата'
            }),
            'work_format': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Местоположение'
            }),
            'employment_type': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'title': 'Название вакансии',
            'description': 'Описание',
            'required_skills': 'Требуемые навыки',
            'required_experience': 'Требуемый опыт (лет)',
            'salary': 'Зарплата',
            'work_format': 'Формат работы',
            'status': 'Статус',
            'location': 'Местоположение',
            'employment_type': 'Тип занятости',
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название навыка'
            })
        }
        labels = {
            'name': 'Название навыка'
        }