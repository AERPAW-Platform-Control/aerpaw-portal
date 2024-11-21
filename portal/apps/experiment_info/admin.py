from django.contrib import admin
from portal.apps.experiment_info.models import GAExperimentFormData, CustomExperimentFormData

# Register your models here.
admin.site.register(GAExperimentFormData)
admin.site.register(CustomExperimentFormData)