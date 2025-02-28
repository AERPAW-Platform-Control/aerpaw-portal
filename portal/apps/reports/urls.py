from django.urls import path

from portal.apps.reports.views import ReportView

urlpatterns = [
    path('', ReportView.as_view(), name='reports_home')
]