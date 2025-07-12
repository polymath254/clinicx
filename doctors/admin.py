from django.contrib import admin
from .models import DoctorProfile

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty')
    search_fields = ('user__email', 'user__username', 'specialty')
    list_filter = ('specialty',)
