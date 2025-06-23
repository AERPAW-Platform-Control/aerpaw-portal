from django.contrib import admin
from portal.apps.error_handling.models import AerpawError

class AerpawErrorAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General Information', {
            'fields': ('id', 'uuid',  'datetime')
        }),
        ('Error Detials', {
            'fields': ('user', 'type', 'traceback')
        }),
        ('Error Messaging', {
            'fields': ('displayed', 'message')
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_by', 'resolved_datetime', 'resolved_description')
        })
    )
    readonly_fields = ('id', 'uuid', 'datetime')



    
# Register your models here.
admin.site.register(AerpawError, AerpawErrorAdmin)
