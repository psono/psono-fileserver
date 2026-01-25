from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework import status
import socket
import os
from urllib.parse  import urlparse
from restapi.utils import APIServer, get_storage
from restapi.utils import get_os_username

def is_socket_open(host, port, timeout=5.0):
    """
    Tests if a socket is open or not and returns True or raises an error otherwise

    :param host:
    :type host:
    :param port:
    :type port:
    :param timeout:
    :type timeout:
    :return:
    :rtype:
    """
    with socket.create_connection((host, port), timeout):
        pass
    return True

def test_config():


    if len(settings.SECRET_KEY) == 0:
        return {
            'error': 'SECRET_KEY empty. Please generate the parameters according to the documentation.'
        }

    print('Success: SECRET_KEY configuration found.')


    if len(settings.PRIVATE_KEY) == 0:
        return {
            'error': 'PRIVATE_KEY empty. Please generate the parameters according to the documentation.'
        }

    print('Success: PRIVATE_KEY configuration found.')


    if len(settings.PUBLIC_KEY) == 0:
        return {
            'error': 'PUBLIC_KEY empty. Please generate the parameters according to the documentation.'
        }

    print('Success: PUBLIC_KEY configuration found.')


    if len(settings.SERVER_URL) == 0:
        return {
            'error': 'SERVER_URL empty. Please generate the parameters according to the documentation.'
        }

    print('Success: SERVER_URL configuration found.')


    if len(settings.SERVER_PUBLIC_KEY) == 0:
        return {
            'error': 'SERVER_PUBLIC_KEY empty. Please generate the parameters according to the documentation.'
        }

    print('Success: SERVER_PUBLIC_KEY configuration found.')


    if len(settings.CLUSTER_ID) == 0:
        return {
            'error': 'CLUSTER_ID empty. Please generate the parameters according to the documentation.'
        }

    print('Success: CLUSTER_ID configuration found.')


    if len(settings.CLUSTER_PRIVATE_KEY) == 0:
        return {
            'error': 'CLUSTER_PRIVATE_KEY empty. Please generate the parameters according to the documentation.'
        }

    print('Success: CLUSTER_PRIVATE_KEY configuration found.')


    if len(settings.HOST_URL) == 0:
        return {
            'error': 'HOST_URL empty. Please generate the parameters according to the documentation.'
        }

    print('Success: HOST_URL configuration found.')


    if len(settings.SHARDS) == 0:
        return {
            'error': 'SHARDS array empty. You have to specify at least one shard.'
        }

    print('Success: SHARDS configuration found.')

    try:
        parsed_server_url = urlparse(settings.SERVER_URL)
    except ValueError:
        return {
            'error': '  - Error: SERVER_URL seems to have an invalid format'
        }

    print('  - Success: SERVER_URL format seems to be correct')

    if parsed_server_url.port is not None:
        port = parsed_server_url.port
    elif parsed_server_url.scheme == 'https':
        port = 443
    elif parsed_server_url.scheme == 'http':
        port = 80
    else :
        return {
            'error': '  - Error: Could not parse port from SERVER_URL'
        }

    domain = parsed_server_url.netloc

    if ':' in domain:
        domain, _ = domain.split(':')

    try:
        port = int(port)
    except ValueError:
        return {
            'error': '  - Error: Invalid port "' + port + '". Please check your SERVER_URL and correct the port.'
        }

    print('  - Success: Your SERVER_URL port is an integer.')

    if port < 1 or port > 65534:
        return {
            'error': '  - Error: Port "' + str(port) + '" out of range. The port should be between 0 and 65535.'
        }

    print('  - Success: Your SERVER_URL port is in the correct range.')

    try:
        is_socket_open(domain, port)
    except socket.gaierror:
        return {
            'error': '  - Error: Host "' + domain + '" not known. Please check the spelling and that the server can resolve it.'
        }
    except socket.timeout:
        return {
            'error': '  - Error: Host or port does not exist or firewall seems to be blocking connections (host: ' + domain + ' port: ' + str(
                port) + ' unreachable). Modify SERVER_URL if necessary.'
        }

    print('  - Success: Host resolved')
    print('  - Success: Host and port exist and firewall seems to allow connections.')

    shards = []

    for shard in settings.SHARDS:

        if not shard.get('shard_id', False):
            return {
                'error': 'Error: Please add shard_id to shards in your settings.yml'
            }

        print('Testing shard ' + shard.get('shard_id') +':')

        if shard.get('shard_id').lower() in shards:
            return {
                'error': '  - Error: Duplicate of a shard id found (' + shard.get('shard_id').lower() + '). Shard IDs should be unique.'
            }

        shards.append(shard.get('shard_id').lower())

        if shard.get('read', None) is None:
            return {
                'error': '  - Error: Please add an read to the shard config in your settings.yml.'
            }

        print('  - Success: Required property read present')

        if shard.get('write', None) is None:
            return {
                'error': '  - Error: Please add an write to the shard config in your settings.yml.'
            }

        print('  - Success: Required property write present')

        if shard.get('delete', None) is None:
            return {
                'error': '  - Error: Please add an delete to the shard config in your settings.yml.'
            }

        print('  - Success: Required property delete present')

        if shard.get('engine', None) is None:
            return {
                'error': '  - Error: Please add an engine to the shard config in your settings.yml.'
            }

        print('  - Success: Required property engine present')

        if not isinstance(shard['engine'], dict):
            return {
                'error': '  - Error: The engine property needs to be of type dict in the shard config in your settings.yml.'
            }

        print('  - Success: property engine has the right type')

        if shard['engine'].get('class', None) is None:
            return {
                'error': '  - Error: Please add a class property to the engine in your shard config in your settings.yml.'
            }

        print('  - Success: Required property class present')

        if shard['engine'].get('kwargs', None) is None:
            return {
                'error': '  - Error: Please add a kwargs property to the engine in your shard config in your settings.yml.'
            }

        print('  - Success: Required property kwargs present')

        if shard['engine'].get('class', None) == 'local':
            if 'location' not in shard['engine'].get('kwargs', {}):
                return {
                    'error': '  - Error: Please add a location property to the engine\'s kwargs in your shard config in your settings.yml.'
                }

            print('  - Success: Required property location in your engine\'s kwargs present.')

            if 'location' not in shard['engine'].get('kwargs', {}):
                return {
                    'error': '  - Error: Please add a location property to the engine\'s kwargs in your shard config in your settings.yml.'
                }

            print('  - Success: Required property location in your engine\'s kwargs present.')

        storage = get_storage(shard['engine'])

        target_path = os.path.join('testconfig', 'test.txt')

        original_content = b'test'
        target_path = storage.save(target_path, ContentFile(original_content))

        if not storage.exists(target_path):
            return {
                'error': '  - Error: Stored testfile does not exist with user ' + get_os_username() + '.'
            }
        print('  - Success: Test file successfully created with user ' + get_os_username() + '.')

        content = storage.open(target_path).read()

        if content != original_content:
            print(content)
            print(original_content)
            return {
                'error': '  - Error: Content of the stored testfile does not match the written content.'
            }

        content = storage.delete(target_path)

        if storage.exists(target_path):
            return {
                'error': '  - Error: Stored testfile still exists after delete with user ' + get_os_username() + '.'
            }
        print('  - Success: Stored test file successfully deleted with user ' + get_os_username() + '.')

    r = APIServer.alive()
    if r.status_code == 401:
            return {
                'error': '  - Error: Connection to server was refused by the server with a permission denied (Status {response.status_code}) and the following message: {response.text}'.format(response=r)
            }

    if not status.is_success(r.status_code):
            return {
                'error': '  - Error: Connection to server was refused by the server with a Status {response.status_code} and the following message: {response.text}'.format(response=r)
            }

    print('  - Success: Connection to server and authorization successful.')


    return {}