from django.core.files.base import ContentFile

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser
from ..app_settings import UploadSerializer
import os


class UploadView(GenericAPIView):
    parser_classes = (MultiPartParser,)
    permission_classes = (AllowAny,)
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')
    throttle_scope = 'transfer'

    def get(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):

        serializer = UploadSerializer(data=request.data, context=self.get_serializer_context())

        if not serializer.is_valid():

            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        chunk = serializer.validated_data['chunk']
        storage = serializer.validated_data['storage']
        hash_checksum = serializer.validated_data['hash_checksum']

        target_path = os.path.join(hash_checksum[0:2], hash_checksum[2:4], hash_checksum[4:6], hash_checksum[6:8], hash_checksum)

        if not storage.exists(target_path):
            storage.save(target_path, ContentFile(chunk.read()))

        return Response({}, status=status.HTTP_200_OK)

    def delete(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)