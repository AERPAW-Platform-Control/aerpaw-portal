from django.urls import path

from portal.apps.profiles.views import profile, user_not_found

urlpatterns = [
    path('', profile, name='profile'),
    path('notfound', user_not_found, name='user_not_found')
]
