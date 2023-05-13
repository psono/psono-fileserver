
import os
import re

from rest_framework import status
from django.conf import settings
from rest_framework import serializers, exceptions

from ..utils import get_ip, APIServer, get_storage
from ..fields import UUIDField


class DownloadSerializer(serializers.Serializer):
    file_transfer_id = UUIDField(required=True)
    ticket = serializers.CharField(required=True)
    ticket_nonce = serializers.CharField(required=True, max_length=64)

    def validate(self, attrs: dict) -> dict:

        file_transfer_id = attrs.get('file_transfer_id')
        ticket = attrs.get('ticket')
        ticket_nonce = attrs.get('ticket_nonce')

        r = APIServer.authorize_download({
            'file_transfer_id': str(file_transfer_id),
            'ticket': ticket,
            'ticket_nonce': ticket_nonce,
            'ip_address': get_ip(self.context['request']),
        })

        if status.is_server_error(r.status_code):
            msg = "Server is offline."
            raise exceptions.ValidationError(msg)

        if not r.json_decrypted:
            if settings.DEBUG:
                print(f"{r.status_code}: {r.text}")
            msg = "Server returned un-decryptable response."
            raise exceptions.ValidationError(msg)

        non_field_errors = r.json_decrypted.get('non_field_errors', None)
        if non_field_errors:
            msg = '; '.join(non_field_errors)
            raise exceptions.ValidationError(msg)

        if not status.is_success(r.status_code):
            msg = "Unknown error reported by server."
            raise exceptions.ValidationError(msg)

        shard_id = r.json_decrypted.get('shard_id', None)
        hash_checksum = r.json_decrypted.get('hash_checksum', None)

        if shard_id is None:
            msg = "Shard ID is missing."
            raise exceptions.ValidationError(msg)

        if hash_checksum is None:
            msg = "Hash is missing."
            raise exceptions.ValidationError(msg)

        if not re.match('^[0-9a-f]*$', hash_checksum, re.IGNORECASE):
            msg = 'HASH_CHECKSUM_NOT_IN_HEX_REPRESENTATION'
            raise exceptions.ValidationError(msg)

        if shard_id not in settings.SHARDS_DICT:
            msg = "Unknown Shard ID"
            raise exceptions.ValidationError(msg)

        shard_config = settings.SHARDS_DICT[shard_id]

        storage = get_storage(shard_config['engine'])

        target_path = os.path.join(hash_checksum[0:2], hash_checksum[2:4], hash_checksum[4:6], hash_checksum[6:8], hash_checksum)
        if not storage.exists(target_path):

            APIServer.revoke_download({
                'file_transfer_id': file_transfer_id,
                'ticket': ticket,
                'ticket_nonce': ticket_nonce,
                'ip_address': get_ip(self.context['request']),
            })

            msg = "CHUNK_NOT_AVAILABLE"
            raise exceptions.ValidationError(msg)

        attrs['chunk'] = storage.open(target_path)
        attrs['hash_checksum'] = hash_checksum

        return attrs
