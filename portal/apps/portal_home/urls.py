from django.urls import path

from portal.apps.portal_home.views import home_view

urlpatterns = [
    path('', home_view, name='home'),
]