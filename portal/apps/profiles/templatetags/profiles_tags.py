import os
from datetime import datetime, timezone

import jwt
from django import template

register = template.Library()


@register.filter
def token_expiry(token_jwt):
    token_json = jwt.decode(
        jwt=token_jwt,
        key=os.getenv('DJANGO_SECRET_KEY'),
        algorithms=["HS256"],
        options={"verify_aud": False, "verify_signature": False}
    )
    ts = int(token_json.get('exp'))
    utc_date = datetime.fromtimestamp(ts, tz=timezone.utc)

    return utc_date


@register.filter
def profile_check(user_profile):
    try:
        employer = user_profile.get('employer', None)
        position = user_profile.get('position', None)
        if not employer or employer.casefold() == 'none':
            return False
        if not position or position.casefold() == 'none':
            return False
        return True
    except Exception as exc:
        print(exc)
        return False
