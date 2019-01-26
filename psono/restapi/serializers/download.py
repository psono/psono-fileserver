from rest_framework import status
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.files.storage import get_storage_class
from rest_framework import serializers, exceptions

from ..utils import get_ip, APIServer

import os


class DownloadSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, max_length=128)
    ticket = serializers.CharField(required=True)
    ticket_nonce = serializers.CharField(required=True, max_length=64)

    def validate(self, attrs: dict) -> dict:

        token = attrs.get('token')
        ticket = attrs.get('ticket')
        ticket_nonce = attrs.get('ticket_nonce')

        r = APIServer.authorize_download({
            'token': token,
            'ticket': ticket,
            'ticket_nonce': ticket_nonce,
            'ip_address': get_ip(self.context['request']),
        })

        if status.is_server_error(r.status_code):
            msg = _("Server is offline.")
            raise exceptions.ValidationError(msg)

        if not status.is_success(r.status_code):
            msg = _("Server is offline.")
            raise exceptions.ValidationError(msg)

        shard_id = r.json_decrypted.get('shard_id', None)
        hash_blake2b = r.json_decrypted.get('hash_blake2b', None)

        if shard_id is None:
            msg = _("Shard ID is missing.")
            raise exceptions.ValidationError(msg)

        if hash_blake2b is None:
            msg = _("Blake2b hash is missing.")
            raise exceptions.ValidationError(msg)

        if shard_id not in settings.SHARDS_DICT:
            msg = _("Unknown Shard ID")
            raise exceptions.ValidationError(msg)

        shard_config = settings.SHARDS_DICT[shard_id]

        storage = get_storage_class(settings.AVAILABLE_FILESYSTEMS[shard_config['engine']['class']])(**shard_config['engine']['kwargs'])

        target_path = os.path.join(hash_blake2b[0:2], hash_blake2b[2:4], hash_blake2b[4:6], hash_blake2b[6:8], hash_blake2b)
        if not storage.exists(target_path):
            msg = _("CHUNK_NOT_AVAILABLE")
            raise exceptions.ValidationError(msg)

        attrs['chunk'] = storage.open(target_path)
        attrs['hash_blake2b'] = hash_blake2b

        return attrs
