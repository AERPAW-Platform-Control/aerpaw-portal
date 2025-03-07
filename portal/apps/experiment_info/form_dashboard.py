import pandas as pd
from datetime import datetime
from uuid import uuid4
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.utils import timezone
from rest_framework.exceptions import NotFound
from rest_framework.request import Request

from portal.apps.projects.views import project_detail
from portal.apps.error_handling.error_dashboard import new_error
from portal.apps.experiment_info.models import ExperimentFormData, FieldTrip
from portal.apps.experiment_info.forms import FieldTripForm
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.experiments.api.viewsets import ExperimentViewSet
from portal.apps.resources.models import AerpawResource
from portal.apps.users.models import AerpawUser, AerpawRolesEnum
from portal.apps.user_messages.user_messages import send_portal_mail_from_message

def create_canonical_experiment(request, project_id):
    print('creating new general availibility experiment')
    print('request.POST.get("urgency")', request.POST.get('urgency'))
    print("request.POST.getlist('location')", request.POST.get('location'))
    try:
        api_request = Request(request=HttpRequest())
        api_request.user = request.user
        api_request.method = 'POST'
        api_request.data.update({
            'project_id': project_id,
            'description': request.POST.get('goal'),
            'name': request.POST.get('title')
        })
        new_experiment = ExperimentViewSet()
        exp = new_experiment.create(api_request)
        
        exp_info = ExperimentFormData()
        exp_info.experiment_type = ExperimentFormData.ExperimentType.CANONICAL
        exp_info.experiment = AerpawExperiment.objects.get(id=exp.data.get("experiment_id"))
        exp_info.title = request.POST.get('title')
        exp_info.host_institution = request.POST.get('host_institution') if request.POST.get('host_institution') else None
        exp_info.lead_experimenter = request.POST.get('lead_experimenter') if request.POST.get('lead_experimenter') else None
        exp_info.lead_email = request.POST.get('lead_email') if request.POST.get('lead_email') else None
        exp_info.is_urgent = request.POST.get('urgency') if request.POST.get('urgency') != 'null' else None 
        exp_info.sponsored_project = request.POST.get('sponsored_project') if request.POST.get('sponsored_project') != 'null' else None
        exp_info.grant_number = request.POST.get('grant_number') if request.POST.get('grant_number') != 'null' else None
        exp_info.keywords = request.POST.get('keywords') if request.POST.get('keywords') else None
        exp_info.location = request.POST.get('location') if request.POST.get('location') else None
        exp_info.is_shared = request.POST.get('is_shared') if request.POST.get('is_shared') else ExperimentFormData.ExtendedBoolean.NOT_SURE
        exp_info.public_url = request.POST.get('sharable_url') if request.POST.get('sharable_url') != 'null' else None
        exp_info.goal = request.POST.get('goal') if request.POST.get('goal') else None
        exp_info.vehicle_behavior = request.POST.get('vehicle_behavior') if request.POST.get('vehicle_behavior') else None
        exp_info.uuid = uuid4()
        exp_info.save()
        return exp
    
    except Exception as exc:
        new_error(exc, request.user)
        print(f'Exception in portal.apps.experiment_info.form_dashboard create_canonical_experiment: {exc}')

def save_non_canonical_experiment_info(request, project_id):
    print('Creating new non-canonical experiment')

    

    try:
        exp_info = ExperimentFormData()
        exp_info.experiment_type = ExperimentFormData.ExperimentType.NON_CANONICAL
        exp_info.title = request.POST.get('title')
        exp_info.host_institution = request.POST.get('host_institution') if request.POST.get('host_institution') else None
        exp_info.lead_experimenter = request.POST.get('lead_experimenter') if request.POST.get('lead_experimenter') else None
        exp_info.lead_email = request.POST.get('lead_email') if request.POST.get('lead_email') else None
        exp_info.is_urgent = request.POST.get('urgency') if request.POST.get('urgency') != 'null' else None 
        exp_info.sponsored_project = request.POST.get('sponsored_project') if request.POST.get('sponsored_project') != 'null' else None
        exp_info.grant_number = request.POST.get('grant_number') if request.POST.get('grant_number') != 'null' else None
        exp_info.keywords = request.POST.get('keywords') if request.POST.get('keywords') != 'null' else None
        exp_info.location = request.POST.get('location') if request.POST.get('location') != 'null' else None
        exp_info.public_url = request.POST.get('sharable_url') if request.POST.get('sharable_url') != 'null' else None
        exp_info.goal = request.POST.get('goal') if request.POST.get('goal') != 'null' else None
        exp_info.vehicle_behavior = request.POST.get('vehicle_behavior') if request.POST.get('vehicle_behavior') != 'null' else None
        exp_info.description = request.POST.get('description') if request.POST.get('description') else None
        exp_info.byod_hardware = request.POST.get('byod_hardware') if request.POST.get('byod_hardware') != 'null' else None
        exp_info.byod_software = request.POST.get('byod_software') if request.POST.get('byod_software') != 'null' else None
        exp_info.questions = request.POST.get('questions') if request.POST.get('questions') != 'null' else None
        exp_info.uuid = uuid4()
        exp_info.save()
        return {'success':True, 'experiment_info':exp_info}
    
    except Exception as exc:
        new_error(exc, request.user)
        print(f'Exception in portal.apps.experiment_info.form_dashboard save_non_canonical_experiment_info: {exc}')

def save_custom_experiment_info(request, project_id):
    print('Creating new custom experiment')
    try: 
        exp_info = ExperimentFormData()
        exp_info.experiment_type = ExperimentFormData.ExperimentType.CUSTOM
        exp_info.title = request.POST.get('title')
        exp_info.host_institution = request.POST.get('host_institution') if request.POST.get('host_institution') else None
        exp_info.lead_experimenter = request.POST.get('lead_experimenter') if request.POST.get('lead_experimenter') else None
        exp_info.lead_email = request.POST.get('lead_email') if request.POST.get('lead_email') else None
        exp_info.description = request.POST.get('description') if request.POST.get('description') else None
        exp_info.byod_hardware = request.POST.get('byod_hardware') if request.POST.get('byod_hardware') != 'null' else None
        exp_info.byod_software = request.POST.get('byod_software') if request.POST.get('byod_software') != 'null' else None
        exp_info.questions = request.POST.get('questions') if request.POST.get('questions') != 'null' else None
        exp_info.sponsored_project = request.POST.get('sponsored_project') if request.POST.get('sponsored_project') != 'null' else None
        exp_info.grant_number = request.POST.get('grant_number') if request.POST.get('grant_number') != 'null' else None
        exp_info.uuid = uuid4()
        exp_info.save()
        return {'success':True, 'experiment_info':exp_info}
    except Exception as exc:
        new_error(exc, request.user)
        print(f'Exception in portal.apps.experiment_info.form_dashboard save_custom_experiment_info: {exc}')

def notify_aerpaw_ops(request, experiment_info, experiment_type: str):
    print('sending message to aerpaw-ops')
    try:
        lead_experimenter_id = AerpawUser.objects.filter(email=experiment_info.lead_email)
    except Exception as exc:
        new_error(exc, request.user)
        print(f'Exception in portal.apps.experiment_info.form_dashboard notify_aerpaw_ops: {exc}')

    recieved_by = [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]  # aerpaw_ops?
    """ recieved_by.append(lead_experimenter_id)
    recieved_by.append(request.user.id) """

    message_subject = ''
    message_body = ''

    if experiment_type == 'canonical':
        if experiment_info.public_url != None:
            public_url = 'Yes'
        else:
            public_url = 'No'
        if experiment_info.grant_number != None:
            grant_number = 'Yes'
        else:
            grant_number = 'No'
        
        message_subject = 'New Experiment Created {}'.format(experiment_info.title)
        message_body = """
The following experiment has been created successfully!

    Short experiment title:
        {0}

    Provide the name of your host institution:
        {1}

    Provide the title of your sponsored project under which you are carrying this experiment:
        {2}

    Is there a grant number for this project?:
        {3}

    If applicable, what is the grant number for the project:
        {4}

    Name of the lead experimenter:
        {5}

    Contact email of the lead experimenter:
        {6}

    Provide 3 to 5 keywords that describes your experiment:
        {7}

    In a few sentences, please describe the goal of your intended experiment:
        {8}

    Identify your experiment location:
        {9}

    Do you have any urgency for carrying out the over-the-air testbed experiments:
        {10}

    Can the data collected from the experiment be shared publicly?:
        {11}

    If available, please provide a link to the website that will be hosting the experiment data (e.g. Github, IEEE Dataport):
        {12}

    Please specify the expected behavior of the vehicles (if any) in your experiment:
        {13}

Thank you,
    Aerpaw Operations Team
""".format(
    experiment_info.title,
    experiment_info.host_institution,
    experiment_info.sponsored_project,
    grant_number,
    experiment_info.grant_number,
    experiment_info.lead_experimenter,
    experiment_info.lead_email,
    experiment_info.keywords,
    experiment_info.goal,
    experiment_info.location,
    experiment_info.is_urgent,
    public_url,
    experiment_info.public_url,
    experiment_info.vehicle_behavior,
    )
        
    if experiment_type == 'non_canonical' or experiment_type == 'non_canonical_ga':
        if experiment_info.public_url != None:
            public_url = 'Yes'
        else:
            public_url = 'No'
        if experiment_info.grant_number != None:
            grant_number = 'Yes'
        else:
            grant_number = 'No'
        
        message_subject = 'Non-Canonical Experiment Request'
        message_body = """
New request for the creation of the following non-canonical experiment:

    Short experiment title:
        {0}

    Provide the name of your host institution:
        {1}

    Provide the title of your sponsored project under which you are carrying this experiment:
        {2}

    Is there a grant number for this project?:
        {3}

    If applicable, what is the grant number for the project:
        {4}

    Name of the lead experimenter:
        {5}

    Contact email of the lead experimenter:
        {6}

    Provide 3 to 5 keywords that describes your experiment:
        {7}

    In a few sentences, please describe the goal of your intended experiment:
        {8}

    Identify your experiment location:
        {9}

    Do you have any urgency for carrying out the over-the-air testbed experiments:
        {10}

    Can the data collected from the experiment be shared publicly?:
        {11}

    If available, please provide a link to the website that will be hosting the experiment data (e.g. Github, IEEE Dataport):
        {12}

    Please specify the expected behavior of the vehicles (if any) in your experiment:
        {13}

    Describe your intended experiment in one or more paragraphs
        {14}

    Describe any BYOD hardware that you may be planning to use during your experiment and how they may be interacting with other equipment and features of the AERPAW platform.
        {15}

    Describe the radio, traffic, and vehicle software that you are planning to use during your experiment. Can be BYOD or AERPAW software
        {16}

    If you have any questions for the AERPAW team, please list them here. The AERPAW team will review your request, and if needed, will arrange a follow up online meeting to discuss your request further, before confirming whether or not your request can be presently accommodated in the platform.
        {17}

A member of the Aerpaw Ops team will reach out to you within a few days for further instruction.

Thank you,
    Aerpaw Operations Team
""".format(
    experiment_info.title,
    experiment_info.host_institution,
    experiment_info.sponsored_project,
    grant_number,
    experiment_info.grant_number,
    experiment_info.lead_experimenter,
    experiment_info.lead_email,
    experiment_info.keywords,
    experiment_info.goal,
    experiment_info.location,
    experiment_info.is_urgent,
    public_url,
    experiment_info.public_url,
    experiment_info.vehicle_behavior,
    experiment_info.description,
    experiment_info.byod_hardware,
    experiment_info.byod_software,
    experiment_info.questions,
    )
        
    print('')
    print(f'message body= \n{message_body}')
    print('')
    kwargs={'received_by':recieved_by, 'message_subject':message_subject, 'message_body':message_body}
    sent_mail = send_portal_mail_from_message(request=request, **kwargs)
    if sent_mail == True:
        print('Email sent!!')

def new_experiment_form_dashboard(request, project_id):
    print('request.POST= ', request.POST)
    user = request.user
    context = {
        'project_id':project_id,
        'user':request.user
        }
    
    if 'submit_experiment' in request.POST:
        print(f'Experiment Info=  {request.POST}')
        experiment_type = request.POST.get('submit_experiment')
        
        if experiment_type == 'canonical':
            new_experiment = create_canonical_experiment(request, project_id)
            return {'experiment_id': new_experiment.data.get('experiment_id'), 'experiment_type':experiment_type, 'redirect':'experiment_detail'}

        elif experiment_type == 'non_canonical_ga':
            new_non_canonical_info = save_non_canonical_experiment_info(request, project_id)
            if new_non_canonical_info['success'] == True:
                print('send email to ops')
                notify_aerpaw_ops(request, experiment_info=new_non_canonical_info['experiment_info'], experiment_type='non_canonical_ga')
            context['experiment_type'] = 'non-canonical'
            return {'template': render_to_string('experiment_info/new_experiment_form/non_canonical_success.html', context)}

        elif experiment_type == 'non_canonical':
            new_non_canonical_info = save_non_canonical_experiment_info(request, project_id)
            if new_non_canonical_info['success'] == True:
                print('send email to ops')
                notify_aerpaw_ops(request, experiment_info=new_non_canonical_info['experiment_info'], experiment_type='non_canonical')
                context['experiment_type'] = 'non-canonical'
                return {'template': render_to_string('experiment_info/new_experiment_form/non_canonical_success.html', context)}

        elif experiment_type == 'custom':
            new_custom_experiment_info = save_custom_experiment_info(request, project_id)
            if new_custom_experiment_info['success'] == True:
                print('send email to ops')
                notify_aerpaw_ops(request, experiment_info=new_custom_experiment_info['experiment_info'], experiment_type='custom')
            context['experiment_type'] = 'custom'
            return {'template': render_to_string('experiment_info/new_experiment_form/non_canonical_success.html', context)}
    
    else:
        return {'template':render_to_string('experiment_info/new_experiment_form/general_availibility_form.html', context)}
    
def upload_old_form_data():
    dframe = pd.read_excel('Old Create Experiment Google Form Data.xlsx')
    for row_index, row in dframe.iterrows():
        ser = pd.Series(row)
        is_urgent = True if ser.iloc[10] == 'YES' else False
        exp_fd = ExperimentFormData.objects.filter(old_form_row_number=row_index+2)
        if len(exp_fd) == 0:
            exp_fd = ExperimentFormData(
                old_form_row_number=row_index+2,
                title=ser.iloc[1] if not pd.isna(ser.iloc[1]) else 'None provided',
                host_institution=ser.iloc[2] if not pd.isna(ser.iloc[2]) else None,
                sponsored_project=ser.iloc[3] if not pd.isna(ser.iloc[3]) else None,
                grant_number=ser.iloc[4] if not pd.isna(ser.iloc[4]) else None,
                lead_experimenter=ser.iloc[5] if not pd.isna(ser.iloc[5]) else None,
                lead_email=ser.iloc[6] if not pd.isna(ser.iloc[6]) else None,
                keywords=ser.iloc[7] if not pd.isna(ser.iloc[7]) else 'None provided',
                goal=ser.iloc[8] if not pd.isna(ser.iloc[8]) else 'None provided',
                location=str(ser.iloc[9]).lower(),
                is_urgent=is_urgent,
                is_shared=ser.iloc[11] if not pd.isna(ser.iloc[11]) else 'NO',
                public_url=ser.iloc[12] if not pd.isna(ser.iloc[12]) else None,
                vehicle_behavior=ser.iloc[13] if not pd.isna(ser.iloc[13]) else 'None provided'
            )
            
<<<<<<< Updated upstream
            exp_fd.save()        
    upload_fieldtrips()

def get_fieldtrip_operators(op_names: list):
    print(f'op_ids {op_names}')
    user_operators = AerpawUser.objects.filter(groups__name=AerpawRolesEnum.OPERATOR.value).distinct()
    print('Operators =', [f'{operator.first_name} {operator.last_name}' for operator in user_operators])
    for name in op_names:
        if name == 'Ozgur':
            op = 'oozdemi@ncsu.edu' 
        elif name == 'Sudhanva':
            op = 'snagara9@ncsu.edu'
        elif name == 'Keshav':
            op = 'bkeshav1@asu.edu'
        elif name == 'John':
            op = 'jckesle2@ncsu.edu'
        elif name == 'Mihai':
            op = 'mlsichit@ncsu.edu'
        elif name == 'Tom Z':
            op = 'tjzajkow@ncsu.edu'
        elif name == 'Anil':
            op = 'agurses@ncsu.edu'
        elif name == 'Thomas':
            op = 'mlsichit@ncsu.edu'
        elif name == 'Thomas H.':
            op = 'mlsichit@ncsu.edu'
        elif name == 'Shreyas':
            op = ''
        elif name == 'Tom H.':
            op = 'mlsichit@ncsu.edu'
        elif name == 'Sarah':
            op = ''
        elif name == 'Mike':
            op = 'mbarts@ncsu.edu'
        elif name == 'Eli':
            op = ''
        elif name == 'Asokan':
            op = 'aram2@ncsu.edu'
        elif name == 'Jeffin':
            op = ''
        elif name == 'Niall':
            op = 'npmullan@ncsu.edu'
        elif name == 'Vishwas':
            op = ''
        elif name == 'Ken':
            op = ''
        elif name == 'Corey':
            op = ''
        elif name == 'Sainath':
            op = ''
        elif name == 'Cole':
            op = ''
        elif name == 'Evan':
            op = ''
        elif name == 'Ismail':
            op = 'iguvenc@ncsu.edu'

def upload_fieldtrips():
    dframe = pd.read_excel('FieldTrips.xlsx')
    user_operators = AerpawUser.objects.filter(groups__name=AerpawRolesEnum.OPERATOR.value).distinct()
    
    print('Operators =', [f'{operator.first_name} {operator.last_name}' for operator in user_operators])
    for row_index, row in dframe.iterrows():
        ser = pd.Series(row)
        # Gets the ExperimentFormData instances for each FieldTrip row
        row_numbers = [int(row_number) for row_number in ser.iloc[0].split(',')]
        exp_fds = ExperimentFormData.objects.filter(old_form_row_number__in = row_numbers)

        # Gets the Aerpaw Operators from the FieldTrip sheet
        operators = ser.iloc[8]
        get_fieldtrip_operators(operators)
        # Gets the Fixed Nodes from the FieldTrip sheet
        fixed_nodes = [AerpawResource.objects.get(name=node.strip()) for node in str(ser.iloc[12]).split(',') if not pd.isna(ser.iloc[12])]
        print(f'Fixed nodes = {[node.name for node in fixed_nodes]}')

        # gets the site location
        location = FieldTrip.AerpawSite.OTHER
        if str(ser.iloc[14]) == 'Lake Wheeler':
            location = FieldTrip.AerpawSite.LAKE_WHEELER
        elif str(ser.iloc[14]) == 'Centennial Campus':
            location = FieldTrip.AerpawSite.CENTENNIAL_CAMPUS


        field_trip = FieldTrip()
        field_trip.number_of_fixed_nodes = int(ser.iloc[1]) if not pd.isna(ser.iloc[1]) else 0
        field_trip.number_of_portable_nodes = int(ser.iloc[2]) if not pd.isna(ser.iloc[2]) else 0
        field_trip.LAMs = int(ser.iloc[3]) if not pd.isna(ser.iloc[3]) else 0
        field_trip.SAMs = int(ser.iloc[4]) if not pd.isna(ser.iloc[4]) else 0
        field_trip.rovers = int(ser.iloc[5]) if not pd.isna(ser.iloc[5]) else 0
        field_trip.helikite = int(ser.iloc[6]) if not pd.isna(ser.iloc[6]) else 0
        field_trip.person_hours = int(ser.iloc[7]) if not pd.isna(ser.iloc[7]) else 0
        field_trip.list_of_operators = str(ser.iloc[8]) if not pd.isna(ser.iloc[8]) else None
        field_trip.experiment_date = str(ser.iloc[9]).split(' ')[0]
        field_trip.start_time = str(ser.iloc[10]) if not pd.isna(ser.iloc[10]) else None
        field_trip.end_time = str(ser.iloc[11]) if not pd.isna(ser.iloc[11]) else None
        field_trip.radio_hardware = str(ser.iloc[13]) if not pd.isna(ser.iloc[13]) else None
        field_trip.site = location
        field_trip.comments = str(ser.iloc[15]) if not pd.isna(ser.iloc[15]) else None
        field_trip.save()
        field_trip.experiment_form.add(*exp_fds)
        field_trip.fixed_nodes_used.add(*fixed_nodes)

def field_trip_form(experiment_id):
    experiment_form_data = ExperimentFormData.objects.filter(experiment=experiment_id) if len(ExperimentFormData.objects.filter(experiment=experiment_id)) >0 else None
    if experiment_form_data:
        form = FieldTripForm(initial={'experiment_form':experiment_form_data})
    else:
<<<<<<< Updated upstream
        form = FieldTripForm()
    return form        
        
def new_field_trip(request):
    print(f'\nnew_field_trip request= {request.data}')
    try:
        exp_form_data = ExperimentFormData.objects.get(experiment__id=request.data.get('experiment_id'))
    except Exception as exc:
        new_error(exc, request.user)
        exp_form_data = None
    
    ft = FieldTrip()
    ft.number_of_fixed_nodes = request.data.get('number_of_fixed_nodes')[0]
    ft.number_of_portable_nodes = request.data.get('number_of_portable_nodes')[0]
    ft.LAMs = request.data.get('LAMs')[0]
    ft.SAMs = request.data.get('SAMs')[0]
    ft.rovers = request.data.get('rovers')[0]
    ft.helikite = request.data.get('helikite')[0]
    ft.person_hours = request.data.get('person_hours')[0]
    ft.experiment_date = request.data.get('experiment_date')[0]
    ft.start_time = request.data.get('start_time')[0]
    ft.end_time = request.data.get('end_time')[0]
    ft.radio_hardware = request.data.get('radio_hardware')[0]
    ft.site = request.data.get('site')[0]
    ft.comments = request.data.get('comments')[0]
    ft.save()

    if exp_form_data:
        ft.experiment_form.add(exp_form_data)
    for fn in request.data.get('fixed_nodes_used'):
        ft.fixed_nodes_used.add(fn)
    for op in request.data.get('operators'):
        ft.operators.add(op)
    print(f'Field Trip = {ft.operators.all()}')


    
    
