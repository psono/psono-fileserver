from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import get_storage_class

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from ..parsers import FileUploadParser
from ..app_settings import UploadSerializer
import os
import pyblake2


class UploadView(GenericAPIView):
    parser_classes = (FileUploadParser,)
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

        # shard_id = serializer.validated_data['shard_id']
        shard_id = '338b17b6-07d1-432c-ab46-732044074f68'

        shard_config = settings.SHARDS_DICT[shard_id]
        # TODO IMPORTANT. Enforce hex in hash_blake2b
        # TODO Test user quota
        # TODO Test if shard exist
        # TODO Test if write is allwoed for this shard
        # TODO Test if write is allwoed for this IP


        storage = get_storage_class(settings.AVAILABLE_FILESYSTEMS[shard_config['engine']['class']])(**shard_config['engine']['kwargs'])

        file_content = request.data['file'].read()
        request.data['file'].seek(0)

        hash_blake2b = pyblake2.blake2b(file_content).hexdigest()

        target_path = os.path.join(hash_blake2b[0:2], hash_blake2b[2:4], hash_blake2b)

        if not storage.exists(target_path):
            storage.save(target_path, ContentFile(request.data['file'].read()))

        return Response({}, status=status.HTTP_200_OK)

    def delete(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)