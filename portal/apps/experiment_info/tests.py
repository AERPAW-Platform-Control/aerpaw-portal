import pandas as pd
from django.test import TestCase
from .models import ExperimentFormData, FieldTrip
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.users.models import AerpawUser


FD_FILE = 'Old Create Experiment Google Form Data.xlsx'
FT_FILE = 'FieldTrips.xlsx'

def fdTest():
    print('Testing the number of FDs with experiment #830')
    file = pd.read_excel(FD_FILE)
    form_datas = ExperimentFormData.objects.all()
    experiments = AerpawExperiment.objects.all()
    experiment_names = [exp.name for exp in experiments]
    fd_titles = [fd.title for fd in form_datas]
    form_data_830 = 0
    form_data_other = 0

    fds_830 = 0
    fds_other = 0

    no_exp = 0
    exp_exists = 0
    mutli_entries = 0

    mutli_titles = []
    for row_index, row in file.iterrows():
        ser = pd.Series(row)
        lead = str(ser.iloc[5]).split(' ')
        experiment_creator = AerpawUser.objects.filter(first_name=lead[0], last_name=lead[len(lead)-1]).first()

        exp_fd = ExperimentFormData.objects.filter(old_form_row_number=row_index+2)

        experiment = AerpawExperiment.objects.filter(name=ser.iloc[1], experiment_creator=experiment_creator).first()
        if experiment != None: 
            fds_other += 1
        else: 
            fds_830 += 1

    for fd in form_datas:
        if fd.experiment == None:
            no_exp += 1
            if fd.title in experiment_names:
                exp_exists += 1
        elif fd.experiment.id == 830:
            form_data_830 += 1
        else:
            form_data_other += 1
        
        title_count = 0
        for title in fd_titles:
            if title == fd.title:
                title_count+=1
        if title_count > 1:
            mutli_entries+=1
            if title not in mutli_titles:
                mutli_titles.append((fd.id, fd.title))


    if form_data_830 == fds_830 and form_data_other == fds_other:
        return True
    else:
        print(f'Total= {len(form_datas)}')
        print(f'FormData 830= {form_data_830}')
        print(f'FormData Other= {form_data_other}')
        print(f'No Exp= {no_exp}')
        print(f'Exp exists= {exp_exists}')
        print(f'multi entries= {mutli_entries}')
        print(f'mutli titles= {mutli_titles}')
        print(f'number of multi titles= {len(mutli_titles)}')
        print(f'fds_830= {fds_830}')
        print(f'fds_other= {fds_other}')
        
def match_form_data_to_experiment():
    form_datas = ExperimentFormData.objects.all()
    experiments = AerpawExperiment.objects.all()
    experiment_titles = [exp.name for exp in experiments]
    forms_w_exp=0
    no_exp = 0
    experiment_exists = 0
    experiment_exists_list = []
    no_exp_list = []
    old_form_count = 0
    old_form_w_exp = 0
    for fd in form_datas:
        if fd.experiment:
           forms_w_exp +=1
        if not fd.experiment and fd.title in experiment_titles:
            experiment_exists+=1
        if not fd.experiment:
            no_exp+=1
            no_exp_list.append(fd)
        if fd.old_form_row_number:
            old_form_count+=1
            if fd.experiment != None:
                old_form_w_exp+=1
        if not fd.experiment and fd.title in experiment_titles:
            experiment_exists_list.append(fd)
    data = {
        'total_forms': [len(form_datas)],
        'forms_w_exp': [forms_w_exp],
        'no_exp': [no_exp],
        'exp_exists': [experiment_exists],
        'old_form_exp': [old_form_count],
        'old_form_w_exp': [old_form_w_exp],
        'non_canonical_forms': [len(experiment_exists_list)],

    }
    df = pd.DataFrame(data)
    
    if forms_w_exp+old_form_count+len(experiment_exists_list) == len(form_datas):
        print(df)
        return True
    else:
        print(df)
        
        return no_exp_list
    
def get_old_forms(form_datas: ExperimentFormData)->list:
    old_forms = []
    for fd in form_datas:
        if fd.old_form_row_number:
            old_forms.append(fd)
    return old_forms

def set_form_experiments():
    form_datas = ExperimentFormData.objects.all()
    fds_w_no_exp = [fd for fd in form_datas if fd.experiment == None]
    fds_w_exp = [fd for fd in form_datas if fd.experiment!=None]
    fds_exp_ids = [fd.id for fd in fds_w_exp]
    experiments = list(AerpawExperiment.objects.all())
    exp_ids = [exp.id for exp in experiments]
    #remove all experiments that are already linked to a form
    print(f'number of experiments= {len(experiments)}')
    for fd in fds_w_exp:
        if fd.experiment in experiments:
            experiments.remove(fd.experiment)
    print(f'number of experiments= {len(experiments)}')
    #check for duplicate names in experiments
    duplicates = list(filter(lambda x: experiments.count(x.name)>1, experiments))
    if len(duplicates) > 0:
        print(f' duplicate experiment names found\n{duplicates}')
    else:
        print('No duplicates found!')
        #set the experiment field to the experiment if the experiment's name is the same as the form's experiment title
        catch_all = AerpawExperiment.objects.get(id=830)
        number_of_linked_exps = []
        for fd in fds_w_no_exp:
            fd.experiment = catch_all
        print(f'Number of Linked Forms= {len(number_of_linked_exps)}')
    
def get_forms_with_existing_experiments(form_datas: ExperimentFormData)->list:
    #check for experiment with the same name as fds
    #check fd experiments with experiment ids with experiments above to make sure theyre not dulicated
    #if theyre not duplicated, add the experiment to the fd
    forms_with_existing_experiments = []
    experiments = AerpawExperiment.objects.all()
    experiment_titles = [exp.name for exp in experiments]
    for fd in form_datas:
        if fd.experiment and fd.experiment.name in experiment_titles:
            experiment_titles.remove(fd.experiment.name)
        if not fd.experiment and fd.title in experiment_titles:
            forms_with_existing_experiments.append(fd)
    return forms_with_existing_experiments
        
def fieldTrips():
    fts = FieldTrip.objects.all()
    total = len(fts)
    exp = 0
    no_exp = 0
    form = 0
    for ft in fts:
        if ft.experiment:
            exp+=1
        if not ft.experiment:
            no_exp+=1
        if ft.experiment_form:
            form+=1
    data = {
        'Total FTs':total,
        'Has Experiment': exp,
        'No Experiment': no_exp,
        'Has Form': form,
    }
    results = pd.DataFrame(data)
    return results        

def fieldTripsMatchForms():
    fts = FieldTrip.objects.all()
    fds = ExperimentFormData.objects.all()
    old_fds = [fd for fd in fds if fd.old_form_row_number]

    #check that all old forms are linked to a field trip
    for ft in fts:
        if ft.experiment_form:
            for form in ft.experiment_form.all():
                if form in old_fds:
                    old_fds.remove(form)

    if len(old_fds) == 0:
        return True
    else:
        for fd in old_fds:
            print(f'Old Form: {fd.id}')

def fieldTripsMatchExp():
    fts = FieldTrip.objects.all()
    count = 0
    for ft in fts:
        if ft.experiment:
            count+=1
    if count == len(fts):
        return True
    else:
        return False
    
def match_ft_exp_fd():
    fts = FieldTrip.objects.all().order_by('id')
    fds = ExperimentFormData.objects.all()
    exps = AerpawExperiment.objects.all()
    file = pd.read_excel('FieldTrips.xlsx')
    row_numbers = []
    fds_by_row = []
    matched_fts_and_fds = []
    error_count = 0
    #get the row numbers from the excel sheet
    for row_index, row in file.iterrows():
        ser = pd.Series(row)
        row_numbers.append([int(row_number) for row_number in ser.iloc[0].split(',')])
    
    #create a list of lists containing forms matching the row numbers
    for row in row_numbers:
        fd_list = []
        for number in row:
            fd_list.append(ExperimentFormData.objects.get(old_form_row_number=int(number)))
        fds_by_row.append(fd_list)
    
    #match the forms to the fts
    for ft_index, ft in enumerate(fts):
        form_count = 0
        for form in fds_by_row[ft_index]:
            if form in ft.experiment_form.all():
                form_count += 1
        if form_count != len(ft.experiment_form.all()):
            print(f'Forms do not match! FieldTrip id {ft.id}')
            error_count+=1
        if form_count == len(ft.experiment_form.all()):
            exp_count = 0
            for form in ft.experiment_form.all():
                for exp in ft.experiment.all():
                    if form.experiment.id == exp.id:
                        exp_count+=1
            if exp_count != len(ft.experiment_form.all()):
                error_count+=1
                print(f'Experiments are consistent in FT and FDs!')
                print(f'FieldTrip id: {ft.id}')
                [print(f'Form id: {form.id}') for form in ft.experiment_form.all()]
    if error_count == 0:
        return 'All Matched Correctly!'



