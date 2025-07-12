from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'datetime', 'status')
    list_filter  = ('status', 'datetime', 'doctor')
    search_fields = ('patient__email', 'doctor__email')
    ordering = ('-datetime',)
