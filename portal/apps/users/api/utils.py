from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from portal.apps.profiles.models import AerpawUserProfile


def get_tokens_for_user(user) -> None:
    """
    Refresh user access_token
    - requires valid refresh_token
    - interacts directly with user object
    """
    profile = AerpawUserProfile.objects.get(pk=user.profile_id)
    refresh = RefreshToken.for_user(user)
    profile.refresh_token = str(refresh)
    profile.access_token = str(refresh.access_token)
    profile.modified_by = user.email
    profile.save()


def refresh_access_token_for_user(user) -> None:
    """
    Generate new access_token / refresh_token pair
    - requires valid access_token
    - interacts directly with user object
    """
    profile = AerpawUserProfile.objects.get(pk=user.profile_id)
    access = AccessToken.for_user(user)
    profile.access_token = str(access)
    profile.save()
    print(access)
