from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from ..permission_classes import AllowLocalhost
from restapi.utils import APIServer

class CleanupChunksView(GenericAPIView):
    permission_classes = (AllowLocalhost,)
    allowed_methods = ('GET', 'OPTIONS', 'HEAD')
    throttle_scope = 'cron'

    def get(self, request, *args, **kwargs):
        """
        Request chunks from the server that can be deleted

        :param request:
        :type request:
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """

        r = APIServer.cleanup_chunks()

        if not status.is_success(r.status_code):
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        print(r.json_decrypted)

        return Response(status=status.HTTP_200_OK)



    def put(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)