import requests

from read_config import CONFIG


def get_proxy_country_code(country_code):
    if country_code in ['PH', 'ID', 'MY', 'TH', 'VN', 'JP', 'SG']:
        return country_code.lower()
    return 'us'


class HttpUtils:

    @staticmethod
    def get_headers():
        return {
            'user-agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        }

    @staticmethod
    def get_proxies(country_code=None):
        local_proxy = CONFIG['proxy'].getboolean('local_proxy')
        luminati_proxy = CONFIG['proxy'].getboolean('luminati_proxy')
        if local_proxy:
            proxy_server = CONFIG['proxy']['local_http_proxy']
            proxies = {"http": proxy_server, "https": proxy_server}
        elif luminati_proxy:
            proxy_server = CONFIG['proxy']['luminati_proxy_server']
            proxy_user = CONFIG['proxy']['luminati_proxy_user']
            if country_code:
                proxy_user += "-country-%s" % get_proxy_country_code(country_code)
            proxy_password = CONFIG['proxy']['luminati_proxy_password']
            proxy_url = "http://%s:%s@%s" % (proxy_user, proxy_password,
                                              proxy_server)
            proxies = {"http": proxy_url, "https": proxy_url}
        else:
            proxies = None
        return proxies

    @staticmethod
    def request_get(url, headers=None, proxies=None, params=None, timeout=60):
        try:
            response = requests.get(
                url,
                headers=headers,
                proxies=proxies,
                params=params,
                timeout=timeout
            )
            return True, response
        except requests.exceptions.Timeout as e:
            return False, 'Request Time Out. info: {}.'.format(str(e))
        except Exception as e:
            return False, 'Error. info: {}.'.format(str(e))

    @staticmethod
    def request_post(url, headers=None, proxies=None, data=None, timeout=60):
        try:
            response = requests.post(
                url,
                headers=headers,
                proxies=proxies,
                data=data,
                timeout=timeout
            )
            return True, response
        except requests.exceptions.Timeout as e:
            return False, 'Request Time Out. info: {}.'.format(str(e))
        except Exception as e:
            return False, 'Error. info: {}.'.format(str(e))

    @staticmethod
    def request_post_json(url, headers=None, proxies=None, data=None, timeout=60):
        try:
            response = requests.post(
                url,
                headers=headers,
                proxies=proxies,
                json=data,
                timeout=timeout
            )
            return True, response
        except requests.exceptions.Timeout as e:
            return False, 'Request Time Out. info: {}.'.format(str(e))
        except Exception as e:
            return False, 'Error. info: {}.'.format(str(e))

