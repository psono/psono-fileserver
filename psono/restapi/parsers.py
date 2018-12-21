"""
Parsers are used to parse the content of incoming HTTP requests.

They give us a generic way of being able to handle various media types
on the request, such as form content or json encoded data.
"""
from __future__ import unicode_literals

from django.conf import settings
from django.core.files.uploadhandler import StopFutureHandlers
from django.http.multipartparser import (
    ChunkIter, parse_header
)

from rest_framework.parsers import JSONParser, BaseParser, DataAndFiles
from rest_framework import renderers
from rest_framework.exceptions import ParseError
import nacl.encoding
import nacl.secret
import json


def decrypt(session_secret_key, text_hex, nonce_hex):

    text = nacl.encoding.HexEncoder.decode(text_hex)
    nonce = nacl.encoding.HexEncoder.decode(nonce_hex)

    secret_box = nacl.secret.SecretBox(session_secret_key, encoder=nacl.encoding.HexEncoder)

    return secret_box.decrypt(text, nonce)


class DecryptJSONParser(JSONParser):
    """
    Decrypts data after JSON deserialization.
    """

    media_type = 'application/json'
    renderer_class = renderers.JSONRenderer

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Takes the incoming JSON object, and decrypts the data
        """

        data = super(DecryptJSONParser, self).parse(stream, media_type, parser_context)

        if 'text' not in data or 'nonce' not in data:
            return data

        decrypted_data = decrypt(stream.auth.secret_key, data['text'], data['nonce'])

        try:
            data = json.loads(decrypted_data.decode())
        except ValueError:
            raise ParseError('Invalid request')

        return data


class FileUploadParser(BaseParser):
    """
    Parser for file upload data.
    """
    media_type = '*/*'
    errors = {
        'unhandled': 'FileUpload parse error - none of upload handlers can handle the stream',
    }

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Treats the incoming bytestream as a raw file upload and returns
        a `DataAndFiles` object.

        `.data` will be None (we expect request body to be a file content).
        `.files` will be a `QueryDict` containing one 'file' element.
        """
        parser_context = parser_context or {}
        request = parser_context['request']
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)
        meta = request.META
        upload_handlers = request.upload_handlers

        # Note that this code is extracted from Django's handling of
        # file uploads in MultiPartParser.
        content_type = meta.get('HTTP_CONTENT_TYPE',
                                meta.get('CONTENT_TYPE', ''))
        try:
            content_length = int(meta.get('HTTP_CONTENT_LENGTH',
                                          meta.get('CONTENT_LENGTH', 0)))
        except (ValueError, TypeError):
            content_length = None

        # See if the handler will want to take care of the parsing.
        for handler in upload_handlers:
            result = handler.handle_raw_input(stream,
                                              meta,
                                              content_length,
                                              None,
                                              encoding)
            if result is not None:
                return DataAndFiles({}, {'file': result[1]})

        # This is the standard case.
        possible_sizes = [x.chunk_size for x in upload_handlers if x.chunk_size]
        chunk_size = min([2 ** 31 - 4] + possible_sizes)
        chunks = ChunkIter(stream, chunk_size)
        counters = [0] * len(upload_handlers)

        for index, handler in enumerate(upload_handlers):
            try:
                handler.new_file(None, 'dummy', content_type,
                                 content_length, encoding)
            except StopFutureHandlers:
                upload_handlers = upload_handlers[:index + 1]
                break

        for chunk in chunks:
            for index, handler in enumerate(upload_handlers):
                chunk_length = len(chunk)
                chunk = handler.receive_data_chunk(chunk, counters[index])
                counters[index] += chunk_length
                if chunk is None:
                    break

        for index, handler in enumerate(upload_handlers):
            file_obj = handler.file_complete(counters[index])
            if file_obj is not None:
                return DataAndFiles({}, {
                    'file': file_obj,
                })

        raise ParseError(self.errors['unhandled'])
