from django import forms
from .models import PersonnelForm, Candidate

class PersonnelFormForm(forms.ModelForm):
    class Meta:
        model = PersonnelForm
        fields = '__all__'
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'passport_issue_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'passport_issued_by': forms.Textarea(attrs={'rows': 2}),
            'additional_info': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class CandidateCreateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['first_name', 'last_name', 'patronymic', 'email', 'phone', 'age', 'experience_years', 'skills']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию',
                'required': True
            }),
            'patronymic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите отчество'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 XXX XXX-XX-XX'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '18',
                'max': '100'
            }),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '50'
            }),
            'skills': forms.SelectMultiple(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'first_name': 'Имя *',
            'last_name': 'Фамилия *',
            'patronymic': 'Отчество',
            'email': 'Email *',
            'phone': 'Телефон',
            'age': 'Возраст',
            'experience_years': 'Опыт работы (лет)',
            'skills': 'Навыки'
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Candidate.objects.filter(email=email).exists():
            raise forms.ValidationError("Кандидат с таким email уже существует")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.startswith('+'):
            raise forms.ValidationError("Номер телефона должен начинаться с '+'")
        return phone

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and (age < 18 or age > 100):
            raise forms.ValidationError("Возраст должен быть от 18 до 100 лет")
        return age

    def clean_experience_years(self):
        experience_years = self.cleaned_data.get('experience_years')
        if experience_years and experience_years > 50:
            raise forms.ValidationError("Опыт работы не может превышать 50 лет")
        return experience_years


class SimpleCandidateForm(forms.ModelForm):
    """Упрощенная форма для создания кандидатов рекрутерами"""

    class Meta:
        model = PersonnelForm
        fields = [
            'last_name', 'first_name', 'patronymic',
            'email', 'phone', 'education', 'specialty',
            'work_experience_total', 'skills'  # ДОБАВИЛИ skills
        ]
        widgets = {
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию',
                'required': True
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя',
                'required': True
            }),
            'patronymic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите отчество'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 XXX XXX-XX-XX'
            }),
            'education': forms.Select(attrs={
                'class': 'form-select'
            }),
            'specialty': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Программная инженерия'
            }),
            'work_experience_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '50'
            }),
            'skills': forms.SelectMultiple(attrs={  # ИЗМЕНИЛИ на SelectMultiple
                'class': 'form-select',
                'size': '6'  # показываем 6 вариантов сразу
            })
        }
        labels = {
            'work_experience_total': 'Опыт работы (лет)',
            'skills': 'Навыки'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем обязательность некоторых полей для рекрутеров
        self.fields['specialty'].required = False
        self.fields['education'].required = False
        self.fields['skills'].required = False  # Навыки не обязательны

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if PersonnelForm.objects.filter(email=email).exists():
            raise forms.ValidationError("Кандидат с таким email уже существует")
        return email


class RecruiterCandidateForm(forms.ModelForm):
    """Форма для создания кандидатов рекрутерами - УПРОЩЕННАЯ"""

    class Meta:
        model = Candidate
        fields = [
            # Основная информация
            'last_name', 'first_name', 'patronymic',
            'email', 'phone', 'age',

            # Профессиональные данные
            'specialization', 'position_level', 'experience_years',
            'employment_status', 'work_format',

            # История работы
            'last_workplace', 'last_position', 'work_period', 'responsibilities',

            # Образование
            'education_level', 'education_institution', 'education_specialty', 'graduation_year',

            # Источник кандидата
            'source', 'assigned_recruiter', 'source_details', 'resume',  # ИСПРАВИЛИ source_details

            # Мотивация и ожидания
            'desired_salary', 'notice_period',

            # Примечания рекрутера
            'recruiter_notes', 'next_actions', 'candidate_features',

            # Навыки
            'skills'
        ]
        widgets = {
            # Основная информация
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию',
                'required': True
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя',
                'required': True
            }),
            'patronymic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите отчество'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 XXX XXX-XX-XX'
            }),

            # Профессиональные данные
            'specialization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Python разработчик'
            }),
            'position_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '50'
            }),
            'employment_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'work_format': forms.Select(attrs={
                'class': 'form-select'
            }),

            # История работы
            'last_workplace': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название компании'
            }),
            'last_position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Должность'
            }),
            'work_period': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: 2020-2023'
            }),
            'responsibilities': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ключевые обязанности и достижения'
            }),

            # Образование
            'education_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'education_institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название учебного заведения'
            }),
            'education_specialty': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Специальность'
            }),
            'graduation_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1950',
                'max': '2030'
            }),

            # Источник кандидата
            'source': forms.Select(attrs={
                'class': 'form-select'
            }),
            'assigned_recruiter': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ФИО рекрутера'
            }),
            'source_details': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ссылка на профиль или детали'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt'
            }),

            # Мотивация и ожидания
            'desired_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Желаемая зарплата'
            }),
            'notice_period': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: 2 недели, сразу'
            }),

            # Примечания рекрутера
            'recruiter_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Заметки для внутреннего использования'
            }),
            'next_actions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Что сделать дальше с кандидатом'
            }),
            'candidate_features': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Сильные стороны, особенности, рекомендации'
            }),

            # Навыки
            'skills': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '6'
            })
        }
        labels = {
            'source_details': 'Детали источника',
            'resume': 'Прикрепить резюме',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Сделаем большинство полей необязательными для быстрого заполнения
        for field in self.fields:
            if field not in ['last_name', 'first_name', 'email']:
                self.fields[field].required = False

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Candidate.objects.filter(email=email).exists():
            raise forms.ValidationError("Кандидат с таким email уже существует")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.startswith('+'):
            raise forms.ValidationError("Номер телефона должен начинаться с '+'")
        return phone

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and (age < 14 or age > 150):
            raise forms.ValidationError("Возраст должен быть от 14 до 150 лет")
        return age

    def clean_experience_years(self):
        experience_years = self.cleaned_data.get('experience_years')
        if experience_years and experience_years > 70:
            raise forms.ValidationError("Опыт работы не может превышать 70 лет")
        return experience_years