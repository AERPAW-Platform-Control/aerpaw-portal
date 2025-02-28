import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
from django.db.models import Q
from django.utils import timezone

from portal.apps.experiments.models import AerpawExperiment, OnDemandSession
from portal.apps.projects.models import AerpawProject
from portal.apps.resources.models import AerpawResource

def get_experiments_by_date_range(start_date=None, end_date=None) ->list[AerpawExperiment]:
    if not start_date:
        start_date = timezone.now() - timedelta(days=365*3)
    if not end_date:
        end_date = timezone.now()
    all_experiments = AerpawExperiment.objects.filter(created__gt=start_date, created__lte=end_date)
    return all_experiments

def resource_usage(experiments: AerpawExperiment) -> dict:
    all_resources = AerpawResource.objects.all().order_by('name')
    resources_by_name = [resource.name for resource in all_resources]
    
    xused = {resource:0 for resource in resources_by_name}
    for exp in experiments:
        for resource in exp.resources.all():
            xused[resource.name] += 1
    return xused

def get_average_session_time(total_seconds):
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, remainder = divmod(remainder, 60)

    return f'{int(days)} days, {int(hours)} hours, {int(minutes)} minutes'

def report_by_institution(start_date=None, end_date=None):
    all_experiments = get_experiments_by_date_range(start_date, end_date)
    
    # projects
    all_projects = []
    for exp in all_experiments:
        if exp.project not in all_projects:
            all_projects.append(exp.project)
    ncsu_projects = [project for project in all_projects if '@ncsu.edu' in project.created_by]
    other_projects = [project for project in all_projects if '@ncsu.edu' not in project.created_by]

    # Experiments
    ncsu_experiments = [exp for exp in all_experiments if '@ncsu.edu' in exp.created_by]
    other_experiments = [exp for exp in all_experiments if '@ncsu.edu' not in exp.created_by]

    # users
    all_users = []
    ncsu_users = []
    other_users = []
    for experiment in all_experiments:
        for member in experiment.experiment_members():
            if member not in all_users:
                all_users.append(member)
            if '@ncsu.edu' not in member.email and member not in other_users:
                other_users.append(member)
            if '@ncsu.edu' in member.email and member not in ncsu_users:
                ncsu_users.append(member)

    # pandas dataframe        
    data = {
        'headings':['# Users', '# Experiments', '# Projects'],
        'ncsu':[len(ncsu_users), len(ncsu_experiments), len(ncsu_projects)],
        'other':[len(other_users), len(other_experiments), len(other_projects)],
        'total':[len(all_users), len(all_experiments), len(all_projects), ],
        }
    df = pd.DataFrame(data)
    return data, df.to_html(index=False, header=True, escape=True, justify='left', col_space=150)

def resource_usage_report(start_date=None, end_date=None):
    xused = resource_usage(get_experiments_by_date_range(start_date, end_date))
    data = {
        'Resources':xused.keys(),
        '# of Times in an Experiment':xused.values(),
    }
    df = pd.DataFrame(data)
    return data, df.to_html(index=False, header=True, escape=True, justify='left', col_space=150)

def fixed_resource_usage_report(start_date=None, end_date=None):
    xused = resource_usage(get_experiments_by_date_range(start_date, end_date))
    fixed_resources = ['LW1', 'LW2', 'LW3', 'LW4', 'LW5', 'CC1', 'CC2', 'CC3']
    data = {
        'headings':['# Experiments'],
        'lw1':[],
        'lw2':[],
        'lw3':[],
        'lw4':[],
        'lw5':[],
        'cc1':[],
        'cc2':[],
        'cc3':[],
        
    }
    [data[resource.casefold()].append(xused[resource]) for resource in fixed_resources]
    df = pd.DataFrame(data)
    return data, df.to_html(index=False, header=True, escape=True, justify='left', col_space=150)

def portable_resource_usage_report(start_date=None, end_date=None):
    xused = resource_usage(get_experiments_by_date_range(start_date, end_date))
    portable_resources = ['LPN1', 'LPN2', 'LPN3', 'LPN4', 'LPN5', 'LPN6', 'SPN-Android', 'SPN-LoRa', 'SPN-Quectel']
    data = {
        'headings':['# Experiments'],
        'LPN1':[],
        'LPN2':[],
        'LPN3':[],
        'LPN4':[],
        'LPN5':[],
        'LPN6':[],
        'SPN-Android':[],
        'SPN-LoRa':[],
        'SPN-Quectel':[],
    }
    [data[resource].append(xused[resource]) for resource in portable_resources]
    data['SPN_Android']=data['SPN-Android']
    data['SPN_LoRa']=data['SPN-LoRa']
    data['SPN_Quectel']=data['SPN-Quectel']
    del data['SPN-Android']
    del data['SPN-LoRa']
    del data['SPN-Quectel']
    df = pd.DataFrame(data)
    return data, df.to_html(index=False, header=True, escape=True, justify='left', col_space=150)

def cloud_resource_usage_report(start_date=None, end_date=None):
    xused = resource_usage(get_experiments_by_date_range(start_date, end_date))
    print(f'xused= {xused}')
    cloud_resources = ['ACN']
    data = {
        'headings':['# Experiment'],
        'acn':[],
    }
    [data[resource.casefold()].append(xused[resource]) for resource in cloud_resources]
    df = pd.DataFrame(data)
    return data, df.to_html(index=False, header=True, escape=True, justify='left', col_space=150)

def lab_usage_report(start_date=None, end_date=None):
    xused = resource_usage(get_experiments_by_date_range(start_date, end_date))
    data = {
        'headings':['# Experiments'],
        'lw':[xused['LW1']],
        'cc':[xused['CC1']]
    }
    df = pd.DataFrame(data)
    return data, df.to_html(index=False, header=True, escape=True, justify='left', col_space=150)

def summarize_session_data(sessions: list[OnDemandSession], session_type: str) -> dict:
    # 'headings':['Completed', 'Incomplete', 'Average Time Spent in Session'],
    data = {
        f'development':[0, 0, 0],
        f'sandbox':[0, 0, 0],
        f'emulation':[0, 0, 0],
        f'testbed':[0, 0, 0],
        f'totals':[0, 0, 0]
    }

    total_dev_time = 0
    total_sandbox_time = 0
    total_emu_time = 0
    total_tb_time = 0

    for session in sessions:
        if session.end_date_time and session.start_date_time:
            if session.session_type == OnDemandSession.SessionType.DEVELOPMENT:
                data['development'][0] += 1
                data['totals'][0] += 1
                total_dev_time = ((session.end_date_time - session.start_date_time).total_seconds() + total_dev_time)
            if session.session_type == OnDemandSession.SessionType.SANDBOX:
                data['sandbox'][0] += 1
                data['totals'][0] += 1
                total_sandbox_time = ((session.end_date_time - session.start_date_time).total_seconds() + total_sandbox_time)
            if session.session_type == OnDemandSession.SessionType.EMULATION:
                data['emulation'][0] += 1
                data['totals'][0] += 1
                total_emu_time = ((session.end_date_time - session.start_date_time).total_seconds() + total_emu_time)
            if session.session_type == OnDemandSession.SessionType.TESTBED:
                data['testbed'][0] += 1
                data['totals'][0] += 1
                total_tb_time = ((session.end_date_time - session.start_date_time).total_seconds() + total_tb_time)
        if not session.end_date_time:
            if session.session_type == OnDemandSession.SessionType.DEVELOPMENT:
                data['development'][1] += 1
                data['totals'][1] += 1
            if session.session_type == OnDemandSession.SessionType.SANDBOX:
                data['sandbox'][1] += 1
                data['totals'][1] += 1
            if session.session_type == OnDemandSession.SessionType.EMULATION:
                data['emulation'][1] += 1
                data['totals'][1] += 1
            if session.session_type == OnDemandSession.SessionType.TESTBED:
                data['testbed'][1] += 1
                data['totals'][1] += 1
    data['development'][2] = get_average_session_time(total_dev_time/data['development'][0]) if data['development'][0] != 0 else 0
    data['sandbox'][2] = get_average_session_time(total_sandbox_time/data['sandbox'][0]) if data['sandbox'][0] != 0 else 0
    data['emulation'][2] = get_average_session_time(total_emu_time/data['emulation'][0]) if data['emulation'][0] != 0 else 0
    data['testbed'][2] = get_average_session_time(total_tb_time/data['testbed'][0]) if data['testbed'][0] != 0 else 0

    session_data = {}
    for key, value in data.items():
        session_data[f'{session_type}_{key}'] = value
        

    return session_data

def session_use_report(start_date=None, end_date=None):
    if not start_date:
        start_date = timezone.now() - timedelta(days=365*3)
    if not end_date:
        end_date = timezone.now()

    ncsu_sessions = OnDemandSession.objects.filter(created__gt=start_date, created__lte=end_date, experiment__created_by__endswith='@ncsu.edu')
    non_ncsu_sessions = OnDemandSession.objects.filter(~Q(experiment__created_by__endswith='@ncsu.edu'), created__gt=start_date, created__lte=end_date)
    all_sessions = [*ncsu_sessions, *non_ncsu_sessions]
    
    
    ncsu_data = summarize_session_data(ncsu_sessions, 'ncsu')
    non_ncsu_data = summarize_session_data(non_ncsu_sessions, 'other')
    total_sessions_data = summarize_session_data(all_sessions, 'all')
    

    table_data = {
        'headings':['Completed', 'Incomplete', 'Average Time Spent in Session']
    }
    table_data.update(ncsu_data)
    table_data.update(non_ncsu_data)
    table_data.update(total_sessions_data)
    

    df = pd.DataFrame(table_data)
    return table_data, df.to_html(index=False, header=True, escape=True, justify='left', col_space=150)

def experiment_stat_report(start_date=None, end_date=None):
    experiments = get_experiments_by_date_range(start_date, end_date)
    data = {
        'Total Experiments': [0],
        '# Grant Funded': [0],
        '# Canonical': [0],
        '# Non-Canonical': [0],
        'Avg. # of Members': [0],
        'Avg. # of Fixed Resources': [0],
        'Avg. # of Portable Resources': [0],
        'Avg. # of LAMs': [0],
        'Avg. # of SAMs': [0],
    }


    df = pd.DataFrame(data)
    return df.to_html(index=False, header=True, escape=True, justify='left', col_space=150)