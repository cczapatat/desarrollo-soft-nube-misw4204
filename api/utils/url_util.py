import os

port_base = os.environ.get('PORT', 6000)
url_host_base = os.environ.get('URL_HOST_BASE', 'http://127.0.0.1:{}'.format(str(port_base)))
url_path_base = '{}/api/videos?path={}'


def create_url_to_public(path) -> str:
    if path is None:
        return ''

    return url_path_base.format(url_host_base, path)
