from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.admin import UserAdmin

# from .forms import AerpawUserCreationForm, AerpawUserChangeForm
from .models import AerpawUser

class AerpawUserResource(resources.ModelResource):
    class Meta:
        model = AerpawUser
class AerpawUserAdmin(UserAdmin, ImportExportModelAdmin, admin.ModelAdmin):
    # add_form = AerpawUserCreationForm
    # form = AerpawUserChangeForm
    model = AerpawUser
    list_display = ["email", "username", ]
    resource_class = AerpawUserResource

admin.site.register(AerpawUser, AerpawUserAdmin)
