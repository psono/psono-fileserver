from django.conf import settings
from django.utils.crypto import constant_time_compare
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions

class CronUser:
    def __init__(self, pk):
        self.pk = pk
    is_authenticated = True

class CronAuthentication(BaseAuthentication):

    def authenticate(self, request):
        cron_access_key = self.get_cron_access_key(request)

        if not cron_access_key or not constant_time_compare(cron_access_key, settings.CRON_ACCESS_KEY) or not settings.CRON_ACCESS_KEY:
            msg = 'Invalid access key'
            raise exceptions.AuthenticationFailed(msg)

        cron_user = CronUser(cron_access_key)
        return cron_user, cron_user

    @staticmethod
    def get_cron_access_key(request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'token':
            msg = 'Invalid token header. No token header present.'
            raise exceptions.AuthenticationFailed(msg)

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)

        return token