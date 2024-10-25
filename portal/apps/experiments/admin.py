# Register your models here.
# Register your models here.
from django.contrib import admin
from portal.apps.experiments.models import AerpawExperiment, UserExperiment, ExperimentSession, OpsSession, CanonicalExperimentResource

admin.site.register(AerpawExperiment)
admin.site.register(UserExperiment)
admin.site.register(ExperimentSession)
admin.site.register(OpsSession)
admin.site.register(CanonicalExperimentResource)
