from datetime import timedelta, datetime
from django.shortcuts import render
from django.views import View
from django.utils import timezone

from portal.apps.users.models import AerpawUser
from portal.apps.reports.report_dashboard import report_by_institution, resource_usage_report, lab_usage_report, session_use_report, fixed_resource_usage_report, portable_resource_usage_report, cloud_resource_usage_report

# Create your views here.
class ReportView(View):

    def get(self, request):
        user = request.user
        is_operator = user.is_operator()
        context = {
            'user':user,
            'is_operator':is_operator,
        }
        return render(request, 'reports/reports_home.html', context)
    
    def post(self, request):
        user = request.user
        is_operator = user.is_operator()

        start_date = timezone.now() - timedelta(days=365*3)
        end_date = timezone.now()
        if request.POST.get('start_date'):
            date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d')
            start_date = timezone.make_aware(date, timezone.get_current_timezone())
        if request.POST.get('end_date'):
            date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d')
            end_date = timezone.make_aware(date, timezone.get_current_timezone())

        institution_data, institution_report_html = report_by_institution(start_date, end_date)
        fixed_resource_data, fixed_resource_usage = fixed_resource_usage_report(start_date, end_date)
        portable_resource_data, portable_resource_usage = portable_resource_usage_report(start_date, end_date)
        cloud_resource_data, cloud_resource_usage = cloud_resource_usage_report(start_date, end_date)
        session_data, session_use = session_use_report(start_date, end_date)



        context = {
            'user':user,
            'is_operator':is_operator,
            'start_date':start_date.strftime("%b %d, %Y"),
            'end_date':end_date.strftime("%b %d, %Y"),
            'institution_data':institution_data,
            'fixed_resource_data':fixed_resource_data, 
            'portable_resource_data':portable_resource_data,
            'cloud_resource_data': cloud_resource_data,
            'session_data':session_data,
        }

        return render(request, 'reports/reports_home.html', context)
