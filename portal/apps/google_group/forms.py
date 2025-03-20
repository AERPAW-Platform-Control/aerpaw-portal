from django import forms
from .models import UserGoogleGroupConsent

class UserGoogleGroupConsentForm(forms.ModelForm):
    consent_given = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class':'form-control'}),
        required=False,
        label='Please add me to the Aerpaw Users Google Group'
    )

    class Meta:
        model = UserGoogleGroupConsent
        fields = ['consent_given']