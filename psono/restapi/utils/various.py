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
    """
    Analyzes a request and returns the ip of the client.

    :param request:
    :return:
    """
    if settings.TRUSTED_IP_HEADER and request.META.get(settings.TRUSTED_IP_HEADER, None):
        return request.META.get(settings.TRUSTED_IP_HEADER, None)
    else:
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        remote_addr = request.META.get('REMOTE_ADDR')
        num_proxies = settings.NUM_PROXIES

        if num_proxies is not None:
            if num_proxies == 0 or xff is None:
                return remote_addr
            addrs = xff.split(',')
            client_addr = addrs[-min(num_proxies, len(addrs))]
            return client_addr.strip()

        return remote_addr