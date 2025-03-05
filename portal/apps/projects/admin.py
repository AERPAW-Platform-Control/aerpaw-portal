# Register your models here.
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from portal.apps.projects.models import AerpawProject, UserProject

# Register your models here.
class AerpawProjectResource(resources.ModelResource):
    class Meta:
        model = AerpawProject
class AerpawProjectAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = AerpawProjectResource
admin.site.register(AerpawProject, AerpawProjectAdmin)
admin.site.register(UserProject)
