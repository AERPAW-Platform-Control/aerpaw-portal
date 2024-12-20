# Register your models here.
from django.contrib import admin
from portal.apps.projects.models import AerpawProject, UserProject

# Register your models here.

admin.site.register(AerpawProject)
admin.site.register(UserProject)
