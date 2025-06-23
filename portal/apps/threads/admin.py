from django.contrib import admin
from portal.apps.threads.models import AerpawThread, ThreadQue

class AerpawThreadAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General Information', {
            'fields': ('uuid', 'user', 'experiment', 'target', 'command'),
        }),
        ('Timing', {
            'fields': ('thread_created', 'is_threaded', 'thread_end'),
        }),
        ('Error Details', {
            'fields': ('exit_code', 'is_error', 'error',),
        }),
        ('Message Details', {
            'fields': ('response', 'displayed', 'message'),
        }),
    )
    readonly_fields = ('thread_created', 'uuid')

# Register your models here.
admin.site.register(AerpawThread, AerpawThreadAdmin)
admin.site.register(ThreadQue)