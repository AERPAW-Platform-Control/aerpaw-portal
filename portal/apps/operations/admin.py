# Register your models here.
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from portal.apps.operations.models import CanonicalNumber

# Register your models here.

class CanonicalNumberResource(resources.ModelResource):
    class Meta:
        model = CanonicalNumber
class CanonicalNumberAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = CanonicalNumberResource
admin.site.register(CanonicalNumber, CanonicalNumberAdmin)