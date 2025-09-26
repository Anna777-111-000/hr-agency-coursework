from django.contrib import admin
from .models import Candidate, Application

class CandidateAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'experience_years', 'created_at']
    list_filter = ['skills', 'experience_years']
    search_fields = ['first_name', 'last_name', 'patronymic', 'email']
    filter_horizontal = ['skills']

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'vacancy', 'status', 'applied_date']
    list_filter = ['status', 'applied_date']
    search_fields = ['candidate__first_name', 'candidate__last_name', 'vacancy__title']

admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Application, ApplicationAdmin)