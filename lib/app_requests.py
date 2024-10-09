# This module is an helper module that ensures that all requests to app
# are done with respect to preliminart app "authentication"
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib.auth.models import User, Group

import requests


class DuckRootGroup:

    def all(self):
        return Group.objects.all()


class DuckRootUser:
    # This is a pseudo user class
    # that helps to represent a root user for internal process

    def __init__(self):
        self.id = 0
        self.username = 'root'

    @property
    def groups(self):
        return DuckRootGroup()


root_user = DuckRootUser()


class AppRequest:

    CSRFTOKEN_ALIAS = 'csrf'

    def __init__(self, user: User):
        self.user = user
        self.csrftoken = None

    def _login_if_needed(self):
        from core.models import UserToken

        has_csrftoken = self.csrftoken and (self.csrftoken_expires_at is None or self.csrftoken_expires_at >= datetime.now(timezone.utc))
        if has_csrftoken:
            return

        user_csrftoken = UserToken.objects.filter(user=self.user, namespace=self.namespace, alias=AppRequest.CSRFTOKEN_ALIAS).first()
        if user_csrftoken:
            self.csrftoken = user_csrftoken.token
            self.csrftoken_expires_at = user_csrftoken.expires_at
            return

        user = self.user
        payload = {
            'user_id': user.id,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'user_name': user.username,
            'namespace': settings.APPLICATION_NAME,
            'group_mapping': dict([(group.id, group.name) for group in user.groups.all()])
        }

        url = self.base_url + self.login_url
        resp = requests.post(url, json=payload)
        data = resp.json()

        csrftoken = self.csrftoken = data['csrftoken']
        csrftoken_expires_at = self.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.SESSION_COOKIE_AGE)

        if user_csrftoken:
            user_csrftoken.token = csrftoken
            user_csrftoken.expires_at = csrftoken_expires_at
            user_csrftoken.save()
        else:
            UserToken(
                user=user,
                namespace=self.namespace,
                alias=AppRequest.CSRFTOKEN_ALIAS,
                token=csrftoken,
                expires_at=csrftoken_expires_at
            ).save()

    def run_method(self, method_name, url, *args, **kwargs):
        self._login_if_needed()
        method = getattr(requests, method_name)

        cookies = kwargs.get('cookies', {})
        cookies['csrftoken'] = self.csrftoken
        kwargs['cookies'] = cookies

        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Token {self.user.auth_token.key}'
        headers['X-CSRFToken'] = self.csrftoken

        if kwargs.get('json', None):
            headers['Content-Type'] = "application/json"

        kwargs['headers'] = headers

        final_url = f'{self.base_url}{url}'
        return method(final_url, *args, **kwargs)

    def get(self, url, *args, **kwargs):
        return self.run_method('get', url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self.run_method('post', url, *args, **kwargs)

    def delete(self, url, *args, **kwargs):
        return self.run_method('delete', url, *args, **kwargs)

    def patch(self, url, *args, **kwargs):
        return self.run_method('patch', url, *args, **kwargs)

    def put(self, url, *args, **kwargs):
        return self.run_method('put', url, *args, **kwargs)


class SearchRequest(AppRequest):

    def __init__(self, url):
        super(SearchRequest, self).__init__(url)
        self.base_url = settings.SEARCHAPP_BACKEND_URL
        self.namespace = 'searchapp'
        self.login_url = '/login/'
