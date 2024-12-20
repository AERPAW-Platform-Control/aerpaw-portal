# Register your models here.
from django.contrib import admin
from portal.apps.experiments.models import AerpawExperiment, UserExperiment, OnDemandSession, ScheduledSession, CanonicalExperimentResource

admin.site.register(AerpawExperiment)
admin.site.register(UserExperiment)
admin.site.register(OnDemandSession)
admin.site.register(ScheduledSession)
