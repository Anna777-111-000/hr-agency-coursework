from django.contrib import admin
from .models import Skill, Vacancy

class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'required_skills']
    search_fields = ['title', 'description']
    filter_horizontal = ['required_skills']

admin.site.register(Skill, SkillAdmin)
admin.site.register(Vacancy, VacancyAdmin)