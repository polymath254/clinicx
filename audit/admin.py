from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display   = ('timestamp','action','content_type','object_id','user')
    list_filter    = ('action','content_type','timestamp','user')
    search_fields  = ('object_id','details')
    readonly_fields= [f.name for f in AuditLog._meta.fields]
