# Register your models here.
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from portal.apps.experiments.models import AerpawExperiment, UserExperiment, OnDemandSession, ScheduledSession, CanonicalExperimentResource

class AerpawExperimentResource(resources.ModelResource):
    class Meta:
        model = AerpawExperiment
class AerpawExperimentAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = AerpawExperimentResource

admin.site.register(AerpawExperiment, AerpawExperimentAdmin)
admin.site.register(UserExperiment)
admin.site.register(OnDemandSession)
admin.site.register(ScheduledSession)
