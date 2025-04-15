from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from django.conf import settings

import os
import shutil
import ntplib

from restapi.utils.various import get_ip


class HealthCheckView(GenericAPIView):
    permission_classes = (AllowAny,)
    allowed_methods = ('GET', 'OPTIONS', 'HEAD')
    throttle_scope = 'health_check'

    def get(self, request, *args, **kwargs):
        """
        Check the health of the application

        :param request:
        :type request:
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """

        unhealthy = False

        time_sync = True
        not_debug_mode = True

        def time_sync_unhealthy():
            c = ntplib.NTPClient()
            try:
                response = c.request(settings.TIME_SERVER, version=3)
            except:
                return True
            return abs(response.offset) > 1

        if settings.HEALTHCHECK_TIME_SYNC_ENABLED and time_sync_unhealthy():
            unhealthy = True
            time_sync = False

        if not settings.DEBUG:
            # unhealthy = True
            not_debug_mode = False

        if unhealthy:
            health_status = status.HTTP_400_BAD_REQUEST

        else:
            health_status = status.HTTP_200_OK

        shard_status = True
        shard_status_info = {}

        min_disk_space = settings.HEALTHCHECK_MIN_DISK_SPACE

        for s in settings.SHARDS:
            if s['engine']['class'] == 'local' and 'location' in s['engine']['kwargs']:
                storage_path = s['engine']['kwargs']['location']
                
                try:
                    # Get disk usage statistics for the path
                    disk_usage = shutil.disk_usage(storage_path)
                    free_space = disk_usage.free
                    
                    # Check if available space is below the minimum threshold
                    if free_space < min_disk_space:
                        shard_status = False
                        shard_status_info[s['shard_id']] = {
                            'status': 'Warning: Low disk space',
                            'free_space_mb': round(free_space / (1024 * 1024), 2),
                            'min_required_mb': round(min_disk_space / (1024 * 1024), 2)
                        }
                except (FileNotFoundError, PermissionError, OSError) as e:
                    # Handle errors in accessing the storage path
                    shard_status = False
                    shard_status_info[s['shard_id']] = {
                        'status': 'Error: Storage path access failed',
                        'error': str(e)
                    }

        return Response({
            'time_sync': {'healthy': time_sync},
            'debug_mode': {'healthy': not_debug_mode},
            'shard_status': {
                'healthy': shard_status,
                'details': shard_status_info,
            },
            '_info': {
                'ip': get_ip(request),

            },
        }, status=health_status)

    def put(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)