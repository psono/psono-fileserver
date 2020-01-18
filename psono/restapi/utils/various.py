import os
from django.conf import settings
from django.core.files.storage import get_storage_class

def get_storage(engine):
    return get_storage_class(settings.AVAILABLE_FILESYSTEMS[engine['class']])(**engine['kwargs'])

def get_os_username():

    os_username = 'unknown'
    try:
        os_username = os.getlogin()
    except: #nosec
        pass

    if os_username:
        return os_username
    else:
        return 'unknown'

def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', None)
    cf_connection_ip = request.META.get('HTTP_CF_CONNECTING_IP', None)

    if cf_connection_ip:
        return cf_connection_ip

    if x_forwarded_for:
        splitted_ip_record = x_forwarded_for.split(',')
        ip_address = splitted_ip_record[0].strip()
    else:
        ip_address = request.META.get('REMOTE_ADDR')

    return ip_address