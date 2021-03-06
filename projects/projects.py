import uuid

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import Project, AerpawUser


def create_new_project(request, form):
    """

    :param request:
    :param form:
    :return:
    """
    project = Project()
    project.uuid = uuid.uuid4()
    project.name = form.data.getlist('name')[0]
    try:
        project.description = form.data.getlist('description')[0]
    except ValueError as e:
        print(e)
        project.description = None

    # project.principal_investigator = AerpawUser.objects.get(
    #     id=int(form.data.getlist('principal_investigator')[0])
    # )

    project.principal_investigator = request.user
    project.save()
    # add principal_investigator to project_members if not already there
    if project.principal_investigator not in project.project_members.all():
        project.project_members.add(project.principal_investigator)
        project.save()

    project.created_by = request.user
    project.created_date = timezone.now()
    project.modified_by = project.created_by
    project.modified_date = project.created_date
    project.save()

    try:
        project_member_email_list = form.data.getlist('add_project_members')[0].split(',')
        update_project_members(project, project_member_email_list)
        project.save()
    except ValueError as e:
        print(e)

    return str(project.uuid)


def update_project_members(project, project_member_email_list):
    """

    :param project:
    :param project_member_id_list:
    :return:
    """
    # clear current project membership
    #project.project_members.clear()
    # add members from project_member_id_update_list
    project.project_pending_member_emails = ''
    project.save()
    updated_pending_email_list=[]
    for member_email in project_member_email_list:
        try:
            project_member = AerpawUser.objects.get(oidc_claim_email=member_email)
            project.project_members.add(project_member)
        except AerpawUser.DoesNotExist:
            updated_pending_email_list.append(member_email)
    
    seen = set()
    unique_list = []
    for email in updated_pending_email_list:
        if email not in seen:
            unique_list.append(email)
            seen.add(email)
    project.project_pending_member_emails = ",".join(str(x) for x in unique_list)
    if project.project_pending_member_emails != '':
        send_pending_memeber_emails(unique_list)

def send_pending_memeber_emails(pending_member_emails_list):
    subject = 'AERPAW project sign up'
    message = 'You received this email because a project PI has added you to the project. Please go to aerpaw.org to login and signup.' 
    email_from = settings.EMAIL_HOST_USER
    recipient_list=pending_member_emails_list
    send_mail( subject, message, email_from, recipient_list )
    

def delete_project_members(project, project_member_id_list):
    """

    :param project:
    :param project_member_id_list:
    :return:
    """
    # clear current project membership
    #project.project_members.clear()
    # add members from project_member_id_update_list
    for member_id in project_member_id_list:
        project_member = AerpawUser.objects.get(id=int(member_id))
        project.project_members.remove(project_member)
    project.save()

def update_existing_project(request, project, form):
    """
    Create new AERPAW Project

    :param request:
    :param form:
    :return:
    """
    project.modified_by = request.user
    project.modified_date = timezone.now()
    project.save()
    try:
        project_member_id_list = form.data.getlist('delete_project_members')
        delete_project_members(project, project_member_id_list)
        project.save()
    except ValueError as e:
        print(e)

    try:
        pending_member_emails = form.data.getlist('add_project_members')[0]
        if project.project_pending_member_emails != '':
            pending_member_emails = project.project_pending_member_emails + ',' + pending_member_emails
        print("pending_member_emails: " + project.project_pending_member_emails)
        if pending_member_emails != '':
            project_member_email_list = pending_member_emails.split(',')
            update_project_members(project, project_member_email_list)
            project.save()
    except ValueError as e:
        print(e)

    return str(project.uuid)


def delete_existing_project(request, project):
    """

    :param request:
    :param project:
    :return:
    """
    try:
        project.delete()
        return True
    except Exception as e:
        print(e)
    return False


def get_project_list(request):
    """

    :param request:
    :return:
    """
    if request.user.is_superuser:
        projects = Project.objects.filter(created_date__lte=timezone.now()).order_by('name')
    else:
        projects = request.user.projects.order_by('name')
    return projects
