from django.conf import settings
import requests
import json
import nacl.encoding
import nacl.secret


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
    def query(endpoint, data=None, headers=None):

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

        r = requests.put(settings.SERVER_URL + endpoint, data=data, verify=settings.SERVER_URL_VERIFY_SSL, headers=headers)

        APIServer._decrypt(r)

        return r