from django import forms

from portal.apps.projects.models import AerpawProject


class CredentialAddForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'size': 60}),
        required=True,
        label='Name',
    )

    credential = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 60}),
        required=True,
        label='Public Key',
    )

    class Meta:
        model = AerpawProject
        fields = ['name', 'credential']


class CredentialGenerateForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'size': 60}),
        required=True,
        label='Name',
    )

    class Meta:
        model = AerpawProject
        fields = ['name']
