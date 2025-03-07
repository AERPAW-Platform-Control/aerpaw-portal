from django import forms

from .models import FieldTrip, ExperimentFormData
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.resources.models import AerpawResource
from portal.apps.users.models import AerpawUser

class FieldTripForm(forms.ModelForm):
    """  
    In experiment_session template indexes
    None - experiment_form (hidden)
    0 - number_of_fixed_nodes
    1- number_of_portable_nodes
    2 - LAMs
    3 - SAMs
    4 - rovers
    5 - helikite
    6 - person_hours
    7 - operators
    8 - experiment_date
    9 - start_time
    10 - end_time
    11 - fixed_nodes_used
    12 - radio_hardware
    13 - site
    14 - comments
    """
    experiment_form = forms.IntegerField(
        label='Experiment Form',
        widget=forms.NumberInput(attrs={'class':'form-control'})
    )
    experiment = forms.IntegerField(
        label='Experiment',
        widget=forms.NumberInput(attrs={'class':'form-control'})
    )
    number_of_fixed_nodes = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class':'form-control'}),
        required=False,
        label='Number of Fixed Nodes'
    )
    number_of_portable_nodes = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class':'form-control'}),
        required=False,
        label='Number of Portable Nodes'
    )
    LAMs = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class':'form-control'}),
        required=False,
        label='Number of LAMs'
    )
    SAMs = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class':'form-control'}),
        required=False,
        label='Number of SAMs'
    )
    rovers = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class':'form-control'}),
        required=False,
        label='Number of Rovers'
    )
    helikite = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class':'form-control'}),
        required=False,
        label='Helikite'
    )
    person_hours = forms.FloatField(
        widget=forms.NumberInput(attrs={'class':'form-control'}),
        required=False,
        label='Person Hours'
    )
    operators = forms.ModelMultipleChoiceField(
        queryset=AerpawUser.objects.filter(username__endswith = '@ncsu.edu').order_by('first_name'),
        widget=forms.CheckboxSelectMultiple(attrs={'class':'form-check-input'}),
        required=False,
        label='Select Operator(s)',
    )
    experiment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type':'date', 'class':'form-control'}),
        label='Date of Experiment',
        required=False,
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class':'form-control'}),
        label='Time Start',
        required=False,
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class':'form-control'}),
        label='Time End',
        required=False,
    )
    fixed_nodes_used = forms.ModelMultipleChoiceField(
        queryset=AerpawResource.objects.filter(resource_type=AerpawResource.ResourceType.AFRN).order_by('name'),
        widget=forms.CheckboxSelectMultiple(attrs={'class':'form-check-input'}),
        label='Fixed Node(s) Used',
        required=False,
    )
    radio_hardware = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 50, 'class':'form-control'}),
        required=False,
        label='Experiment Radio Hardware',
    )
    site = forms.ChoiceField(
        choices=FieldTrip.AerpawSite.choices,
        widget=forms.RadioSelect(attrs={'class':'form-check-input'}),
        label='AERPAW Site',
        required=False,
    )
    comments = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 50, 'class':'form-control'}),
        required=False,
        label='Comments',
    )
    

    class Meta:
        model = FieldTrip
        fields = ['experiment_form', 'experiment', 'number_of_fixed_nodes', 'number_of_portable_nodes', 'LAMs', 'SAMs', 
                  'rovers', 'helikite', 'person_hours', 'operators', 'experiment_date', 'start_time', 
                  'end_time', 'fixed_nodes_used', 'radio_hardware', 'site', 'comments',]

    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['experiment_form'].widget = forms.HiddenInput()
        self.fields['fixed_nodes_used'].label_from_instance = lambda obj: f'{obj.name}'
        self.fields['operators'].label_from_instance = lambda obj: f'{obj.first_name} {obj.last_name}'

class MultipleExpFieldTripForm(forms.ModelForm):
    """  
    In experiment_session template indexes
    None - experiment_form (hidden)
    0 - number_of_fixed_nodes
    1- number_of_portable_nodes
    2 - LAMs
    3 - SAMs
    4 - rovers
    5 - helikite
    6 - person_hours
    7 - operators
    8 - experiment_date
    9 - start_time
    10 - end_time
    11 - fixed_nodes_used
    12 - radio_hardware
    13 - site
    14 - comments
    """
    class TestbedExperiments():
        active_tb_exp = AerpawExperiment.objects.filter(experiment_state = AerpawExperiment.ExperimentState.ACTIVE_TESTBED)

    experiment_form = forms.ModelMultipleChoiceField(
        queryset=ExperimentFormData.objects.filter(experiment__in=TestbedExperiments.active_tb_exp),
        widget=forms.CheckboxSelectMultiple(attrs={'class':'form-check-input'}),
        required=True,
        label='Select Experiment(s)',
    )
    experiment = forms.ModelMultipleChoiceField(
        queryset=TestbedExperiments.active_tb_exp,
        widget=forms.CheckboxSelectMultiple(attrs={'class':'form-check-input'}),
        required=True,
        label='Select Experiment(s)',
    )
    number_of_fixed_nodes = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class':'form-control'}),
        required=False,
        label='Number of Fixed Nodes'
    )
    number_of_portable_nodes = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class':'form-control'}),
        required=False,
        label='Number of Portable Nodes'
    )
    LAMs = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class':'form-control'}),
        required=False,
        label='Number of LAMs'
    )
    SAMs = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class':'form-control'}),
        required=False,
        label='Number of SAMs'
    )
    rovers = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class':'form-control'}),
        required=False,
        label='Number of Rovers'
    )
    helikite = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class':'form-control'}),
        required=False,
        label='Helikite'
    )
    person_hours = forms.FloatField(
        widget=forms.NumberInput(attrs={'class':'form-control'}),
        required=False,
        label='Person Hours'
    )
    operators = forms.ModelMultipleChoiceField(
        queryset=AerpawUser.objects.filter(username__endswith = '@ncsu.edu').order_by('first_name'),
        widget=forms.CheckboxSelectMultiple(attrs={'class':'form-check-input'}),
        required=False,
        label='Select Operator(s)',
    )
    experiment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type':'date', 'class':'form-control'}),
        label='Date of Experiment',
        required=False,
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class':'form-control'}),
        label='Time Start',
        required=False,
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class':'form-control'}),
        label='Time End',
        required=False,
    )
    fixed_nodes_used = forms.ModelMultipleChoiceField(
        queryset=AerpawResource.objects.filter(resource_type=AerpawResource.ResourceType.AFRN).order_by('name'),
        widget=forms.CheckboxSelectMultiple(attrs={'class':'form-check-input'}),
        label='Fixed Node(s) Used',
        required=False,
    )
    radio_hardware = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 50, 'class':'form-control'}),
        required=False,
        label='Experiment Radio Hardware',
    )
    site = forms.ChoiceField(
        choices=FieldTrip.AerpawSite.choices,
        widget=forms.RadioSelect(attrs={'class':'form-check-input'}),
        label='AERPAW Site',
        required=False,
    )
    comments = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 50, 'class':'form-control'}),
        required=False,
        label='Comments',
    )
    

    class Meta:
        model = FieldTrip
        fields = ['experiment_form', 'experiment', 'number_of_fixed_nodes', 'number_of_portable_nodes', 'LAMs', 'SAMs', 
                  'rovers', 'helikite', 'person_hours', 'operators', 'experiment_date', 'start_time', 
                  'end_time', 'fixed_nodes_used', 'radio_hardware', 'site', 'comments',]

    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['experiment_form'].label_from_instance = lambda obj: f'{obj.experiment.id}: {obj.experiment.name}'
        self.fields['fixed_nodes_used'].label_from_instance = lambda obj: f'{obj.name}'
        self.fields['operators'].label_from_instance = lambda obj: f'{obj.first_name} {obj.last_name}'