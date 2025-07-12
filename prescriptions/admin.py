from django.contrib import admin
from .models import Prescription, PrescriptionDrug

class PrescriptionDrugInline(admin.TabularInline):
    model = PrescriptionDrug
    extra = 0
    readonly_fields = ('drug', 'dosage', 'quantity')

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'patient', 'date')
    list_filter  = ('date', 'doctor')
    search_fields = ('doctor__email', 'patient__email')
    inlines       = [PrescriptionDrugInline]
