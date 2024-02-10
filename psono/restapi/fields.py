from rest_framework.serializers import UUIDField as InsecureUUIDField
from rest_framework.serializers import BooleanField as InsecureBooleanField



class UUIDField(InsecureUUIDField):
    # Minimizes Reflected XSS
    default_error_messages = {
        'invalid': 'Is not a valid UUID.',
    }

class BooleanField(InsecureBooleanField):
    # Minimizes Reflected XSS
    default_error_messages = {
        'invalid': 'Is not a valid boolean.'
    }

