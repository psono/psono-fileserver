from django.conf import settings
import requests
import json
import nacl.encoding
import nacl.secret
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class APIServer(object):


    @staticmethod
    def _decrypt(r):

        try:
            json_encrypted = json.loads(r.text)

            text = nacl.encoding.HexEncoder.decode(json_encrypted['text'])
            nonce = nacl.encoding.HexEncoder.decode(json_encrypted['nonce'])

            decrypted_text = settings.SESSION_CRYPTO_BOX.decrypt(text, nonce)
            r.json_decrypted = json.loads(decrypted_text.decode())
        except:
            r.json_decrypted = None



    @staticmethod
    def query(method, endpoint, data=None, headers=None):

        if not data:
            data = {}

        if not headers:
            headers = {}

        if not settings.SERVER_URL_VERIFY_SSL:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        if method == 'POST':
            r = requests.post(settings.SERVER_URL + '/fileserver' + endpoint, json=data, verify=settings.SERVER_URL_VERIFY_SSL, headers=headers, timeout=10.0)
        elif method == 'PUT':
            r = requests.put(settings.SERVER_URL + '/fileserver' + endpoint, json=data, verify=settings.SERVER_URL_VERIFY_SSL, headers=headers, timeout=10.0)
        elif method == 'GET':
            r = requests.get(settings.SERVER_URL + '/fileserver' + endpoint, verify=settings.SERVER_URL_VERIFY_SSL, headers=headers, timeout=10.0)
        else:
            raise Exception

        APIServer._decrypt(r)

        return r


    @staticmethod
    def alive():

        method = 'PUT'
        endpoint = '/alive/'
        data = None
        headers = {
            'Authorization': 'Token ' + settings.FILESERVER_ID,
            'Authorization-Validator': json.dumps({
                'fileserver_info': settings.FILESERVER_INFO,
                'cluster_id': settings.CLUSTER_ID
            })
        }

        return APIServer.query(
            method=method,
            endpoint=endpoint,
            data=data,
            headers=headers,
        )


    @staticmethod
    def cleanup_chunks():

        method = 'GET'
        endpoint = '/chunks/cleanup/'
        data = None
        headers = {
            'Authorization': 'Token ' + settings.FILESERVER_ID,
        }

        return APIServer.query(
            method=method,
            endpoint=endpoint,
            data=data,
            headers=headers,
        )


    @staticmethod
    def cleanup_chunks_confirm(data):

        method = 'POST'
        endpoint = '/chunks/cleanup/'
        headers = {
            'Authorization': 'Token ' + settings.FILESERVER_ID,
        }

        return APIServer.query(
            method=method,
            endpoint=endpoint,
            data=data,
            headers=headers,
        )


    @staticmethod
    def authorize_upload(data):

        method = 'PUT'
        endpoint = '/upload/authorize/'
        headers = {
            'Authorization': 'Token ' + settings.FILESERVER_ID,
        }

        return APIServer.query(
            method=method,
            endpoint=endpoint,
            data=data,
            headers=headers,
        )


    @staticmethod
    def authorize_download(data):

        method = 'PUT'
        endpoint = '/download/authorize/'
        headers = {
            'Authorization': 'Token ' + settings.FILESERVER_ID,
        }

        return APIServer.query(
            method=method,
            endpoint=endpoint,
            data=data,
            headers=headers,
        )


    @staticmethod
    def revoke_download(data):

        method = 'PUT'
        endpoint = '/download/revoke/'
        headers = {
            'Authorization': 'Token ' + settings.FILESERVER_ID,
        }

        return APIServer.query(
            method=method,
            endpoint=endpoint,
            data=data,
            headers=headers,
        )