from rest_framework import status
from django.conf import settings
from rest_framework import serializers, exceptions

import hashlib

from ..utils import get_ip, APIServer, get_storage


class UploadSerializer(serializers.Serializer):

    def validate(self, attrs: dict) -> dict:

        file_transfer_id = self.context['request'].data.get('file_transfer_id', None)
        chunk = self.context['request'].data.get('chunk', None)
        ticket = self.context['request'].data.get('ticket', None)
        ticket_nonce = self.context['request'].data.get('ticket_nonce', None)

        if file_transfer_id is None:
            msg = "File transfer id is required."
            raise exceptions.ValidationError(msg)

        if chunk is None:
            msg = "File is required."
            raise exceptions.ValidationError(msg)

        if ticket is None:
            msg = "Ticket is required."
            raise exceptions.ValidationError(msg)

        if ticket_nonce is None:
            msg = "Ticket nonce is required."
            raise exceptions.ValidationError(msg)

        chunk_content = chunk.read()
        chunk.seek(0)

        chunk_size = len(chunk_content)
        hash_checksum = hashlib.sha512(chunk_content).hexdigest()


        r = APIServer.authorize_upload({
            'file_transfer_id': file_transfer_id,
            'ticket': ticket,
            'ticket_nonce': ticket_nonce,
            'chunk_size': chunk_size,
            'hash_checksum': hash_checksum,
            'ip_address': get_ip(self.context['request']),
        })

        if status.is_server_error(r.status_code):
            msg = "Server is offline."
            raise exceptions.ValidationError(msg)

        if not r.json_decrypted:
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

        if shard_id is None:
            msg = "Shard ID is missing."
            raise exceptions.ValidationError(msg)

        if shard_id not in settings.SHARDS_DICT:
            msg = "Unknown Shard ID"
            raise exceptions.ValidationError(msg)

        shard_config = settings.SHARDS_DICT[shard_id]

        storage = get_storage(shard_config['engine'])

        attrs['storage'] = storage
        attrs['chunk'] = chunk
        attrs['hash_checksum'] = hash_checksum

        return attrs
