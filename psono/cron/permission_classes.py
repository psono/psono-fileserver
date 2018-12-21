from rest_framework.permissions import BasePermission

import ipaddress


class AllowLocalhost(BasePermission):
    """
    Allow any access from localhost.
    """

    def has_permission(self, request, view):
        ip = request.META.get('REMOTE_ADDR')

        return ipaddress.ip_address(ip).is_loopback