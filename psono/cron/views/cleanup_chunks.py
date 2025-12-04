from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny

import os

from ..authentication import CronAuthentication
from restapi.utils import APIServer, get_storage

class CleanupChunksView(GenericAPIView):
    authentication_classes = (CronAuthentication, )
    permission_classes = (AllowAny,)
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


        deleted_chunk_list = []
        for shard_id in r.json_decrypted['shards']:

            if shard_id not in settings.SHARDS_DICT:
                continue

            shard_config = settings.SHARDS_DICT[shard_id]

            if not shard_config['delete']:
                continue

            chunks = r.json_decrypted['shards'][shard_id]

            if len(chunks) < 1:
                continue

            storage = get_storage(shard_config['engine'])

            for hash_checksum in chunks:

                target_path = os.path.join(hash_checksum[0:2], hash_checksum[2:4], hash_checksum[4:6], hash_checksum[6:8], hash_checksum)

                if storage.exists(target_path):
                    storage.delete(target_path)

            deleted_chunk_list.append({
                'shard_id': shard_id,
                'chunks': chunks,
            })

        if len(deleted_chunk_list) > 0:
            r = APIServer.cleanup_chunks_confirm({
                'deleted_chunks': deleted_chunk_list
            })

            if not status.is_success(r.status_code):
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK)



    def put(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)