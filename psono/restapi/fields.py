from django.utils.translation import ugettext_lazy as _
from rest_framework.serializers import UUIDField as InsecureUUIDField
from rest_framework.serializers import BooleanField as InsecureBooleanField
from rest_framework.serializers import NullBooleanField as InsecureNullBooleanField



class UUIDField(InsecureUUIDField):
    # Minimizes Reflected XSS
    default_error_messages = {
        'invalid': _('Is not a valid UUID.'),
    }

class BooleanField(InsecureBooleanField):
    # Minimizes Reflected XSS
    default_error_messages = {
        'invalid': _('Is not a valid boolean.')
    }

class NullBooleanField(InsecureNullBooleanField):
    # Minimizes Reflected XSS
    default_error_messages = {
        'invalid': _('Is not a valid boolean.')
    }
