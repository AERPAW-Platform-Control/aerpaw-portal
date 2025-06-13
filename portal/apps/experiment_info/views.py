import json
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views import View
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.request import Request

from .models import ExperimentFormData, FieldTrip
from .forms import FieldTripForm, MultipleExpFieldTripForm
from portal.apps.error_handling.error_dashboard import new_error
from portal.apps.experiments.models import AerpawExperiment, ScheduledSession
from portal.apps.experiments.api.experiment_sessions import end_scheduled_session, create_experiment_session
from portal.apps.experiments.api.viewsets import ExperimentViewSet

# Create your views here.
class ExperimentFormDataView(View):
    def get(self, request):
        message = None
        user = request.user
        is_operator = user.is_operator()

        experiment_fds = ExperimentFormData.objects.all().order_by('created').reverse()
        context = {
            'message':message,
            'is_operator':is_operator,
            'experiment_fds':experiment_fds,
            'is_operator':is_operator,
        }
        return render(request, 'experiment_info/experiment_from_responses.html', context)
    
    def post(self, request):
        request_body = json.loads(request.body)
        fd = ExperimentFormData.objects.filter(id=int(request_body['formDataId'])).first()

        # get all the fields of the ExperimentFormData model except for reverse relationships
        fields = [field for field in ExperimentFormData._meta.get_fields() if field.concrete]

        # Create a json ready dictionary of the model field name: form data instance value
        fd_data = {field.name:str(getattr(fd, field.name)) for field in fields }
        return JsonResponse(fd_data)

        

class FieldTripView(View):
    def get(self, request):
        message = None
        user = request.user
        is_operator = user.is_operator()
        if is_operator == True:
            field_trips = FieldTrip.objects.all().order_by('experiment_date').reverse()
            form = MultipleExpFieldTripForm
            context={
                'message':message,
                'is_operator':is_operator,
                'field_trips':field_trips,
            }
            return render(request, 'experiment_info/field_trip_dashboard.html', context)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to view errors")
            except PermissionDenied as exc:
                new_error(exc, request.user)

    def post(self, request):
        print('')
        message = None
        user = request.user
        is_operator = user.is_operator()
        if is_operator == True:
            
            if request.method == 'POST':
                print('request= ', request.POST)
                """ 
                Action Items:
                 - save the field trip form
                 - for each experiment 
                    - save the testbed session success
                    and
                    - reinititiate dev 
                    or 
                    - reschedule new testbed session
                    or
                    - not create any new sessions
                """
                experiments = request.POST.getlist('experiment_form')
                successfull_exps = request.POST.getlist('is-success') if 'is-success' in request.POST else []
                exps_new_dev_session = request.POST.getlist('init-development') if 'init-development' in request.POST else []
                exps_new_tb_session = request.POST.getlist('reschedule-testbed') if 'reschedule-testbed' in request.POST else []
                for exp_id in experiments:
                    print()
                    experiment = AerpawExperiment.objects.get(id=int(exp_id))
                    api_request = Request(request=HttpRequest())
                    api_request.user = request.user
                    api_request.method = 'PUT'
                    e = ExperimentViewSet(request=api_request)

                    experiment_fd = ExperimentFormData.objects.get(id=int(exp_id))
                    experiment = experiment_fd.experiment
                    is_success = True if exp_id in successfull_exps else False
                    init_dev = True if exp_id in exps_new_dev_session else False
                    reschedule_tb = True if exp_id in exps_new_tb_session else False
                    
                    if init_dev == True and reschedule_tb == False:
                        print(f'Ending Testbed session and starting Dev session for exp# {experiment.id}')
                        # Ends the current Testbed Session
                        api_request.data.update({
                            'next_state':AerpawExperiment.ExperimentState.SAVED,
                            'is_success':is_success,
                            'session_description':'None',
                        })
                        e.state(api_request, pk=int(experiment.id))
                        
                        # Starts a new development Session - Need to make sure scripts are run to return from testbed session first
                        #api_request.data.update({'next_state':AerpawExperiment.ExperimentState.WAIT_DEVELOPMENT_DEPLOY})
                        #e.state(api_request, pk=int(experiment.id))

                    elif init_dev == False and reschedule_tb == True:
                        print(f'Ending Testbed session and starting new testbed session for exp# {experiment.id}')
                        # Ends the current testbed session and reschedules a new one
                        api_request.data.update({
                            'next_state':AerpawExperiment.ExperimentState.SAVED,
                            'is_success':is_success,
                            'session_description':'None',
                            'reschedule_session':True
                        })
                        e.state(api_request, pk=int(experiment.id))

                    elif init_dev == True and reschedule_tb == True:
                        print(f'Ending Testbed session and Error for exp# {experiment.id}')
                        try:
                            raise ValidationError(detail='Multiple Session Error: Cannot reinitiate development session and reschedule testbed session at the same time')
                        except ValidationError as exc:
                            new_error(exc, request.user)
                        # Ends the current Testbed Session
                        api_request.data.update({
                            'next_state':AerpawExperiment.ExperimentState.SAVED,
                            'is_success':is_success,
                            'session_description':'None',
                        })
                        e.state(api_request, pk=int(experiment.id))
                    else:
                        print(f'Ending Testbed session for exp# {experiment.id}')
                        # Ends the current Testbed Session
                        api_request.data.update({
                            'next_state':AerpawExperiment.ExperimentState.SAVED,
                            'is_success':is_success,
                            'session_description':'None',
                        })
                        e.state(api_request, pk=int(experiment.id))


                form = MultipleExpFieldTripForm(request.POST)
                if form.is_valid():
                    form.save()
                form = MultipleExpFieldTripForm
                field_trips = FieldTrip.objects.all()
            else:    
                field_trips = FieldTrip.objects.all()
                form = MultipleExpFieldTripForm

            context={
                'message':message,
                'is_operator':is_operator,
                'field_trips':field_trips,
            }
            return render(request, 'experiment_info/field_trip_dashboard.html', context)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to view errors")
            except PermissionDenied as exc:
                new_error(exc, request.user)