# Register your models here.
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from portal.apps.resources.models import AerpawResource

# Register your models here.

class AerpawResourceResource(resources.ModelResource):
    class Meta:
        model = AerpawResource
class AerpawResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = AerpawResourceResource
admin.site.register(AerpawResource, AerpawResourceAdmin)
