from django.urls import path
from .views import ExperimentFormDataView, FieldTripView
urlpatterns = [
    path('experiment_form_responses/', ExperimentFormDataView.as_view(), name='experiment_form_responses'),
    path('field_trip_dashboard/', FieldTripView.as_view(), name='field_trip_dashboard'),
]