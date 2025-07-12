from django.contrib import admin
from .models import PatientProfile

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'allergies')
    search_fields = ('user__email', 'user__username')
    list_filter = ('date_of_birth',)
