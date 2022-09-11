from django import forms

from portal.apps.experiment_files.models import ExperimentFile


class ExperimentFileCreateForm(forms.ModelForm):
    file_name = forms.CharField(
        widget=forms.TextInput(attrs={'size': 60}),
        required=True,
        label='File Name',
    )

    file_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 60}),
        required=True,
        label='Notes',
    )

    file_location = forms.CharField(
        widget=forms.TextInput(attrs={'size': 60}),
        required=True,
        label='Full File Path',
    )

    file_type = forms.ChoiceField(
        choices=ExperimentFile.LinkedFileType.choices,
        widget=forms.Select(),
        required=True,
        label='Type',
    )

    class Meta:
        model = ExperimentFile
        fields = ['file_name', 'file_notes', 'file_location', 'file_type', 'is_active']
