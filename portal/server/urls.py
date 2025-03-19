"""portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from portal.apps.credentials.api.viewsets import CredentialViewSet
from portal.apps.error_handling.api.viewsets import AerpawErrorViewset, AerpawThreadViewset
from portal.apps.experiment_files.api.viewsets import ExperimentFileViewSet
from portal.apps.experiments.api.viewsets import CanonicalExperimentResourceViewSet, OnDemandSessionViewSet, \
    ExperimentViewSet, UserExperimentViewSet
from portal.apps.operations.api.viewsets import CanonicalNumberViewSet
from portal.apps.profiles.views import session_expired
from portal.apps.projects.api.viewsets import ProjectViewSet, UserProjectViewSet
from portal.apps.resources.api.viewsets import ResourceViewSet
from portal.apps.user_messages.api.viewsets import UserMessageViewSet
from portal.apps.user_requests.api.viewsets import UserRequestViewSet
from portal.apps.google_group.views import oauth2_callback
from portal.apps.users.api.viewsets import UserViewSet

# Routers provide an easy way of automatically determining the URL conf.
# Ordering is important for overloaded API slugs with differing ViewSet definitions
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'canonical-experiment-resource', CanonicalExperimentResourceViewSet,
                basename='canonical-experiment-resource')
router.register(r'credentials', CredentialViewSet, basename='credentials')
router.register(r'aerpaw-error', AerpawErrorViewset, basename='aerpaw-error')
router.register(r'aerpaw-thread', AerpawThreadViewset, basename='aerpaw-thread')
router.register(r'experiment-files', ExperimentFileViewSet, basename='experiment-files')
router.register(r'experiments', ExperimentViewSet, basename='experiments')
router.register(r'messages', UserMessageViewSet, basename='messages')
router.register(r'p-canonical-experiment-number', CanonicalNumberViewSet, basename='canonical-experiment-number')
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'requests', UserRequestViewSet, basename='requests')
router.register(r'resources', ResourceViewSet, basename='resources')
router.register(r'sessions', OnDemandSessionViewSet, basename='sessions')
router.register(r'user-experiment', UserExperimentViewSet, basename='user-experiment')
router.register(r'user-project', UserProjectViewSet, basename='user-project')
router.register(r'users', UserViewSet, basename='users')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('oauth2callback/', oauth2_callback, name='oauth2_callback'),
    path('accounts/login/', session_expired, name='session_expired'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/', include('django.contrib.auth.urls')),
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('credentials/', include('portal.apps.credentials.urls')),  # credentials app
    path('error_handling/', include('portal.apps.error_handling.urls')),  # error_handling app
    path('operators/experiment-files/', include('portal.apps.experiment_files.urls')),  # experiment_files app
    path('operators/experiment-info/', include('portal.apps.experiment_info.urls')),  # experiment_files app
    path('experiments/', include('portal.apps.experiments.urls')),  # experiments app
    path('google_group/', include('portal.apps.google_group.urls')),  # google_group app
    path('messages/', include('portal.apps.user_messages.urls')),  # user_messages app
    path('profile/', include('portal.apps.profiles.urls')),  # profiles app
    path('projects/', include('portal.apps.projects.urls')),  # projects app
    path('reports/', include('portal.apps.reports.urls')),  # reports app
    path('resources/', include('portal.apps.resources.urls')),  # resources app
    path('requests/', include('portal.apps.user_requests.urls')),  # user_requests app
]
