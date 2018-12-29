

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