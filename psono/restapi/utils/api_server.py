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
            headers = {
                'Authorization': 'Token ' + settings.FILESERVER_ID,
                'Authorization-Validator': json.dumps({
                    'fileserver_info': settings.FILESERVER_INFO,
                    'cluster_id': settings.CLUSTER_ID
                })
            }

        if not settings.SERVER_URL_VERIFY_SSL:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        if method == 'PUT':
            r = requests.put(settings.SERVER_URL + '/fileserver' + endpoint, json=data, verify=settings.SERVER_URL_VERIFY_SSL, headers=headers)
        else:
            raise Exception

        APIServer._decrypt(r)

        return r