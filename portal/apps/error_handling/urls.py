from django.urls import path
from portal.apps.error_handling.views import ErrorHandlingView, ErrorDashboardView

urlpatterns = [
    path('', ErrorHandlingView.as_view(), name='error_handling'),
    path('error_handling', ErrorHandlingView.as_view(), name='error_handling'),
    path('error_dashboard', ErrorDashboardView.as_view(), name='error_dashboard'),
]