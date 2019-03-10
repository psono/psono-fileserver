from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from ..permission_classes import AllowLocalhost
from restapi.utils import APIServer

class PingView(GenericAPIView):
    permission_classes = (AllowLocalhost,)
    allowed_methods = ('GET', 'OPTIONS', 'HEAD')
    throttle_scope = 'cron'

    def get(self, request, *args, **kwargs):
        """
        Sends the health status of the file server to the server.

        :param request:
        :type request:
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """

        r = APIServer.alive()

        if status.is_success(r.status_code):
            return Response(status=status.HTTP_200_OK)
        elif r.status_code == 401:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)



    def put(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)