from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from ..app_settings import DownloadSerializer


class DownloadView(GenericAPIView):
    permission_classes = (AllowAny,)
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')
    throttle_scope = 'transfer'

    def get(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):

        serializer = DownloadSerializer(data=request.data, context=self.get_serializer_context())

        if not serializer.is_valid():

            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        chunk = serializer.validated_data['chunk']
        hash_checksum = serializer.validated_data['hash_checksum']

        response = HttpResponse(FileWrapper(chunk), content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="%s"' % hash_checksum

        return response

    def delete(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)