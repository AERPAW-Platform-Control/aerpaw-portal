from django.contrib import admin
from portal.apps.error_handling.models import AerpawError, AerpawThread

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


class AerpawThreadAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General Information', {
            'fields': ('uuid', 'user', 'experiment', 'action'),
        }),
        ('Timing', {
            'fields': ('thread_start', 'thread_end'),
        }),
        ('Error Details', {
            'fields': ('exit_code', 'is_error', 'error',),
        }),
        ('Message Details', {
            'fields': ('response', 'displayed', 'message'),
        }),
    )
    readonly_fields = ('thread_start', 'uuid')
    
# Register your models here.
admin.site.register(AerpawError, AerpawErrorAdmin)
admin.site.register(AerpawThread, AerpawThreadAdmin)