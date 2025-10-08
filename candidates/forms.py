from django import forms
from .models import PersonnelForm


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
        # Добавляем CSS классы для стилизации
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'