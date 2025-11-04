# candidates/admin.py
from django.contrib import admin
from .models import Candidate, Application, Interview, PersonnelForm

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'specialization', 'experience_years')
    list_filter = ('position_level', 'employment_status', 'work_format')
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'vacancy', 'status', 'applied_date')
    list_filter = ('status',)

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'scheduled_date', 'interview_type', 'status')
    list_filter = ('interview_type', 'status')

@admin.register(PersonnelForm)
class PersonnelFormAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'patronymic', 'education', 'is_approved')
    list_filter = ('education', 'is_approved')