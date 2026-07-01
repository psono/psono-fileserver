from mock import Mock, patch
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIRequestFactory

from .base import APITestCaseExtended
from restapi.serializers.download import DownloadSerializer


class DownloadSerializerTest(APITestCaseExtended):
    """
    Tests for download serializer validation.
    """

    @override_settings(SHARDS_DICT={
        'shard-id': {
            'engine': {
                'class': 'local',
                'kwargs': {},
            },
        },
    })
    @patch('restapi.serializers.download.APIServer.revoke_download')
    @patch('restapi.serializers.download.get_storage')
    @patch('restapi.serializers.download.APIServer.authorize_download')
    def test_missing_chunk_revokes_download_with_string_file_transfer_id(
            self, authorize_download, get_storage, revoke_download):
        """
        Tests that a missing chunk revokes the download with a string file transfer id.
        """

        file_transfer_id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'
        ticket = 'ticket'
        ticket_nonce = 'ticket_nonce'
        hash_checksum = 'a' * 64
        request = APIRequestFactory().post('/download/', REMOTE_ADDR='127.0.0.1')

        authorize_download.return_value = Mock(
            status_code=status.HTTP_200_OK,
            json_decrypted={
                'shard_id': 'shard-id',
                'hash_checksum': hash_checksum,
            },
            text='',
        )
        storage = Mock()
        storage.exists.return_value = False
        get_storage.return_value = storage

        serializer = DownloadSerializer(data={
            'file_transfer_id': file_transfer_id,
            'ticket': ticket,
            'ticket_nonce': ticket_nonce,
        }, context={'request': request})

        self.assertFalse(serializer.is_valid())
        revoke_download.assert_called_once_with({
            'file_transfer_id': file_transfer_id,
            'ticket': ticket,
            'ticket_nonce': ticket_nonce,
            'ip_address': '127.0.0.1',
        })
