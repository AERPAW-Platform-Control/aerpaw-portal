from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from portal.apps.experiment_info.models import ExperimentFormData, FieldTrip


# Register your models here.

    

class ExperimentFormDataResource(resources.ModelResource):
    class Meta:
        model = ExperimentFormData
class ExperimentFormDataAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ExperimentFormDataResource
    fieldsets = (
        ('General Information', {
            'fields': ('id', 'uuid', 'old_form_row_number', 'created', 'title', 'experiment_type', 'experiment', 'is_urgent')
        }),
        ('Experimenter', {
            'fields':( 'lead_experimenter', 'lead_email')
        }),
        ('Institution', {
            'fields': ('host_institution', 'sponsored_project', 'grant_number', 'is_shared', 'public_url')
        }),
        ('Description', {
            'fields': ('location', 'keywords', 'goal', 'description')
        }),
        ('Equipment', {
            'fields': ('vehicle_behavior', 'byod_hardware', 'byod_software')
        }),
        ('Questions for Aerpaw Ops', {
            'fields': ['questions']
        })
    )
    readonly_fields = ('id', 'uuid', 'created')
admin.site.register(ExperimentFormData, ExperimentFormDataAdmin)

class FieldTripResource(resources.ModelResource):
    class Meta:
        model = FieldTrip
class FieldTripAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = FieldTripResource
admin.site.register(FieldTrip, FieldTripAdmin)
