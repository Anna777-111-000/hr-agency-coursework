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