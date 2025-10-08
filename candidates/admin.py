from django.contrib import admin
from .models import Candidate, Application, PersonnelForm  # ДОБАВИТЬ PersonnelForm
@admin.register(PersonnelForm)
class PersonnelFormAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'patronymic', 'birth_date', 'is_approved']
    list_filter = ['is_approved', 'education', 'marital_status']
    search_fields = ['last_name', 'first_name', 'patronymic', 'email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('last_name', 'first_name', 'patronymic', 'birth_date', 'birth_place', 'citizenship')
        }),
        ('Контактная информация', {
            'fields': ('address', 'phone', 'email')
        }),
        ('Образование', {
            'fields': ('education', 'institution', 'specialty', 'graduation_year')
        }),
        ('Семейное положение', {
            'fields': ('marital_status',)
        }),
        ('Паспортные данные', {
            'fields': ('passport_series', 'passport_number', 'passport_issued_by',
                      'passport_issue_date', 'passport_department_code')
        }),
        ('Документы', {
            'fields': ('inn', 'snils')
        }),
        ('Воинский учет', {
            'fields': ('military_duty', 'military_rank', 'military_specialty')
        }),
        ('Трудовая деятельность', {
            'fields': ('work_experience_total', 'work_experience_specialty')
        }),
        ('Дополнительная информация', {
            'fields': ('additional_info',)
        }),
        ('Служебная информация', {
            'fields': ('is_approved', 'created_at', 'updated_at')
        }),
    )