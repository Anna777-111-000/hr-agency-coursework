from django.contrib import admin
from .models import Candidate, PersonnelForm

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'specialization', 'experience_years', 'created_at')
    list_filter = ('position_level', 'employment_status', 'work_format')
    search_fields = ('first_name', 'last_name', 'email')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PersonnelForm)
class PersonnelFormAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'patronymic', 'education', 'candidate_status', 'is_approved', 'created_at')
    list_filter = ('education', 'is_approved', 'candidate_status')
    list_editable = ('candidate_status', 'is_approved')
    search_fields = ('last_name', 'first_name', 'patronymic', 'email')
    readonly_fields = ('created_at', 'updated_at')

    actions = ['mark_approved', 'mark_rejected']

    def mark_approved(self, request, queryset):
        queryset.update(is_approved=True, candidate_status='accepted')
    mark_approved.short_description = "Отметить как одобренные и принятые"

    def mark_rejected(self, request, queryset):
        queryset.update(is_approved=False, candidate_status='rejected')
    mark_rejected.short_description = "Отметить как отклоненные"