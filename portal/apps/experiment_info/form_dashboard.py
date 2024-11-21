from uuid import uuid4
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from rest_framework.request import Request
from portal.apps.projects.views import project_detail
from portal.apps.experiment_info.models import GAExperimentFormData, CustomExperimentFormData
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.experiments.api.viewsets import ExperimentViewSet
from portal.apps.users.models import AerpawUser
from portal.apps.user_messages.user_messages import send_portal_mail_from_message

def create_canonical_experiment(request, project_id):
    print('creating new general availibility experiment')
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
        
        exp_info = GAExperimentFormData()
        exp_info.experiment = AerpawExperiment.objects.get(id=exp.data.get("experiment_id"))
        exp_info.title = request.POST.get('title')
        exp_info.host_institution = request.POST.get('host_institution') if request.POST.get('host_institution') else None
        exp_info.lead_experimenter = request.POST.get('lead_experimenter') if request.POST.get('lead_experimenter') else None
        exp_info.lead_email = request.POST.get('lead_email') if request.POST.get('lead_email') else None
        exp_info.urgency_date = request.POST.get('urgency_date') if request.POST.get('urgency_date') != 'null' else None 
        exp_info.sponsored_project = request.POST.get('sponsored_project') if request.POST.get('sponsored_project') != 'null' else None
        exp_info.grant_number = request.POST.get('grant_number') if request.POST.get('grant_number') != 'null' else None
        exp_info.keywords = request.POST.get('keywords') if request.POST.get('keywords') else None
        exp_info.location = request.POST.getlist('location') if request.POST.getlist('location') else None
        exp_info.public_url = request.POST.get('sharable_url') if request.POST.get('sharable_url') != 'null' else None
        exp_info.goal = request.POST.get('goal') if request.POST.get('goal') else None
        exp_info.vehicle_behavior = request.POST.get('vehicle_behavior') if request.POST.get('vehicle_behavior') else None
        exp_info.uuid = uuid4()
        exp_info.save()
        return exp
    
    except Exception as exc:
        print(f'Exception in portal.apps.experiment_info.form_dashboard create_canonical_experiment: {exc}')

def save_non_canonical_experiment_info(request, project_id):
    print('Creating new non-canonical experiment')
    try:
        exp_info = GAExperimentFormData()
        exp_info.title = request.POST.get('title')
        exp_info.host_institution = request.POST.get('host_institution') if request.POST.get('host_institution') else None
        exp_info.lead_experimenter = request.POST.get('lead_experimenter') if request.POST.get('lead_experimenter') else None
        exp_info.lead_email = request.POST.get('lead_email') if request.POST.get('lead_email') else None
        exp_info.urgency_date = request.POST.get('urgency_date') if request.POST.get('urgency_date') != 'null' else None 
        exp_info.sponsored_project = request.POST.get('sponsored_project') if request.POST.get('sponsored_project') != 'null' else None
        exp_info.grant_number = request.POST.get('grant_number') if request.POST.get('grant_number') != 'null' else None
        exp_info.keywords = request.POST.get('keywords') if request.POST.get('keywords') != 'null' else None
        exp_info.location = request.POST.getlist('location') if request.POST.getlist('location') != 'null' else None
        exp_info.public_url = request.POST.get('sharable_url') if request.POST.get('sharable_url') != 'null' else None
        exp_info.goal = request.POST.get('goal') if request.POST.get('goal') != 'null' else None
        exp_info.vehicle_behavior = request.POST.get('vehicle_behavior') if request.POST.get('vehicle_behavior') != 'null' else None
        exp_info.uuid = uuid4()
        exp_info.save()
        return {'success':True, 'experiment_info':exp_info}
    
    except Exception as exc:
        print(f'Exception in portal.apps.experiment_info.form_dashboard save_non_canonical_experiment_info: {exc}')

def save_custom_experiment_info(request, project_id):
    print('Creating new custom experiment')
    try: 
        exp_info = CustomExperimentFormData()
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
        print(f'Exception in portal.apps.experiment_info.form_dashboard save_custom_experiment_info: {exc}')

def notify_aerpaw_ops(request, experiment_info, experiment_type: str):
    print('sending message to aerpaw-ops')
    try:
        lead_experimenter_id = AerpawUser.objects.filter(email=experiment_info.lead_email)
    except Exception as exc:
        print(f'Exception in portal.apps.experiment_info.form_dashboard notify_aerpaw_ops: {exc}')

    recieved_by = [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]  # aerpaw_ops?
    """ recieved_by.append(lead_experimenter_id)
    recieved_by.append(request.user.id) """

    message_subject = ''
    message_body = ''

    if experiment_type == 'canonical':
        if experiment_info.urgency_date != None:
            urgency_date = 'Yes'
        else:
            urgency_date = 'No'
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

    Please specify when you would desire the experiment to get finalized:
        {11}

    Can the data collected from the experiment be shared publicly?:
        {12}

    If available, please provide a link to the website that will be hosting the experiment data (e.g. Github, IEEE Dataport):
        {13}

    Please specify the expected behavior of the vehicles (if any) in your experiment:
        {14}

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
    urgency_date,
    experiment_info.urgency_date,
    public_url,
    experiment_info.public_url,
    experiment_info.vehicle_behavior,
    )
        
    if experiment_type == 'non_canonical' or experiment_type == 'non_canonical_ga':
        if experiment_info.urgency_date != None:
            urgency_date = 'Yes'
        else:
            urgency_date = 'No'
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

    Please specify when you would desire the experiment to get finalized:
        {11}

    Can the data collected from the experiment be shared publicly?:
        {12}

    If available, please provide a link to the website that will be hosting the experiment data (e.g. Github, IEEE Dataport):
        {13}

    Please specify the expected behavior of the vehicles (if any) in your experiment:
        {14}

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
    urgency_date,
    experiment_info.urgency_date,
    public_url,
    experiment_info.public_url,
    experiment_info.vehicle_behavior,
    )
        

    if experiment_type == 'custom':
        
        message_subject = 'New Request for Custom Experiment'
        message_body = """
New Custom Experiment Request for the following experiment: 

    Name of the lead experimenter
        {0}
        
    Contact email of the lead experimenter
        {1}

    Provide the name of your host institution
        {2}

    Short experiment title
        {3}

    Describe your intended experiment in one or more paragraphs
        {4}

    Describe any BYOD hardware that you may be planning to use during your experiment and how they may be interacting with other equipment and features of the AERPAW platform.
        {5}

    Describe the radio, traffic, and vehicle software that you are planning to use during your experiment. Can be BYOD or AERPAW software
        {6}

    If you have any questions for the AERPAW team, please list them here. The AERPAW team will review your request, and if needed, will arrange a follow up online meeting to discuss your request further, before confirming whether or not your request can be presently accommodated in the platform.
        {7}

A member of the Aerpaw Ops team will reach out to you within a few days for further instruction.

Thank you,
    Aerpaw Operations Team
""".format(
    experiment_info.lead_experimenter,
    experiment_info.lead_email,
    experiment_info.host_institution,
    experiment_info.title,
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

    if 'can' in request.POST:
        context['experiment_type'] = 'canonical'
        return {'template': render_to_string('experiment_info/new_experiment_form/general_availibility_form.html', context)}
    
    if 'non_can_ga' in request.POST:
        context['experiment_type'] = 'non_canonical_ga'
        return {'template':render_to_string('experiment_info/new_experiment_form/general_availibility_form.html', context)}
    
    if 'non_can' in request.POST:
        context['experiment_type'] = 'non_canonical'
        return {'template': render_to_string('experiment_info/new_experiment_form/general_availibility_form.html', context)}
    
    if 'custom' in request.POST:
        context['experiment_type'] = 'custom'
        return {'template':render_to_string('experiment_info/new_experiment_form/custom_experiment_form.html', context)}
    
    if 'submit_experiment' in request.POST:
        print(f'Experiment Info=  {request.POST}')
        experiment_type = request.POST.get('submit_experiment')
        
        match experiment_type:
            case 'canonical':
                new_experiment = create_canonical_experiment(request, project_id)
                return {'experiment_id': new_experiment.data.get('experiment_id'), 'experiment_type':experiment_type, 'redirect':'experiment_detail'}
            
            case 'non_canonical_ga':
                new_non_canonical_info = save_non_canonical_experiment_info(request, project_id)
                if new_non_canonical_info['success'] == True:
                    print('send email to ops')
                    notify_aerpaw_ops(request, experiment_info=new_non_canonical_info['experiment_info'], experiment_type='non_canonical_ga')
                context['experiment_type'] = 'non-canonical'
                return {'template': render_to_string('experiment_info/new_experiment_form/non_canonical_success.html', context)}
            
            case 'non_canonical':
                new_non_canonical_info = save_non_canonical_experiment_info(request, project_id)
                if new_non_canonical_info['success'] == True:
                    print('send email to ops')
                    notify_aerpaw_ops(request, experiment_info=new_non_canonical_info['experiment_info'], experiment_type='non_canonical')
                context['experiment_type'] = 'non-canonical'
                return {'template': render_to_string('experiment_info/new_experiment_form/non_canonical_success.html', context)}
            
            case 'custom':
                new_custom_experiment_info = save_custom_experiment_info(request, project_id)
                if new_custom_experiment_info['success'] == True:
                    print('send email to ops')
                    notify_aerpaw_ops(request, experiment_info=new_custom_experiment_info['experiment_info'], experiment_type='custom')
                context['experiment_type'] = 'custom'
                return {'template': render_to_string('experiment_info/new_experiment_form/non_canonical_success.html', context)}
    
    else:
        return {'template':render_to_string('experiment_info/new_experiment_form/choose_experiment_type.html')}