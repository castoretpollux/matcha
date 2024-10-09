import requests

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin

from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from lib.auth import get_user


class TokenAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/admin/'):
            return None
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b'token':
            request.user = AnonymousUser()
        elif len(auth) == 1 or len(auth) > 2:
            # FIXME : Use translation framework
            raise AuthenticationFailed('Invalid token header. No credentials provided or token string should not contain spaces.')
        else:
            token = auth[1].decode()

            response = requests.post(settings.BACKEND_URL + '/api/user/validate_token/', data={'token': token})
            data = response.json()

            if response.status_code == 200 and data.get('valid'):
                request.user = get_user(user_id=data.get("user_id"))
            else:
                # FIXME : Use translation framework
                raise AuthenticationFailed('Invalid token')
