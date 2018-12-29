from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.files.storage import get_storage_class
from rest_framework import serializers, exceptions

from ..utils import get_ip

import ipaddress
import pyblake2


class UploadSerializer(serializers.Serializer):

    def in_networks(self, ip_address, networks):
        """
        Takes an ip address and and array of networks, each in String representation.
        Will return whether the ip address in one of the network ranges

        :param ip_address:
        :type ip_address:
        :param networks:
        :type networks:
        :return:
        :rtype:
        """

        for network in networks:
            ip_network = ipaddress.ip_network(network)
            if ip_address in ip_network:
                return True

        return False

    def validate(self, attrs: dict) -> dict:

        ip_address = ipaddress.ip_address(get_ip(self.context['request']))

        file = self.context['request'].data.get('file', None)
        hash_blake2b_provided = self.context['request'].data.get('hash_blake2b', None)
        shard_id = self.context['request'].data.get('shard_id', None)

        if file is None:
            msg = _("File is missing.")
            raise exceptions.ValidationError(msg)

        if hash_blake2b_provided is None:
            msg = _("Hash is missing.")
            raise exceptions.ValidationError(msg)

        if shard_id is None:
            msg = _("Shard ID is missing.")
            raise exceptions.ValidationError(msg)

        if shard_id not in settings.SHARDS_DICT:
            msg = _("Unknown Shard ID")
            raise exceptions.ValidationError(msg)

        shard_config = settings.SHARDS_DICT[shard_id]

        if not shard_config['write']:
            msg = _("This shard does not accept writes.")
            raise exceptions.ValidationError(msg)

        has_write_whitelist = len(settings.IP_WRITE_WHITELIST) > 0
        write_blacklisted = self.in_networks(ip_address, settings.IP_WRITE_BLACKLIST)
        write_whitelisted = self.in_networks(ip_address, settings.IP_WRITE_WHITELIST)

        if has_write_whitelist and not write_whitelisted:
            msg = _("Your ip is not whitelisted.")
            raise exceptions.ValidationError(msg)

        if write_blacklisted:
            msg = _("Your ip is blacklisted.")
            raise exceptions.ValidationError(msg)

        # TODO Test user quota

        file_content = file.read()
        file.seek(0)

        hash_blake2b = pyblake2.blake2b(file_content).hexdigest()

        if hash_blake2b_provided != hash_blake2b:
            msg = _("Upload corrupted, hash missmatch.")
            raise exceptions.ValidationError(msg)


        storage = get_storage_class(settings.AVAILABLE_FILESYSTEMS[shard_config['engine']['class']])(**shard_config['engine']['kwargs'])

        attrs['storage'] = storage
        attrs['file'] = file
        attrs['hash_blake2b'] = hash_blake2b

        return attrs
