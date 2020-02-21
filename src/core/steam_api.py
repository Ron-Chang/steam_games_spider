# built-in
import time
import requests
# project
from core.steam_const import OS, STEAM


class SteamAPI:

    default_headers = {
        'user-agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/79.0.3945.130 Safari/537.36'
        )
    }

    @classmethod
    def _request_get_html(cls, url, headers=None):
        if headers:
            cls.default_headers.update(headers)
        error_count = 0
        while True:
            try:
                response = requests.get(url, headers=cls.default_headers)
                if response.status_code != requests.codes.ok:
                    return None
                response.encoding = 'utf8'
                break
            except Exception as e:
                print(f'[LOG       ]| <function: {cls._request_get_html.__name__}> {e}')
                error_count += 1
                if error_count > 100:
                    return None
                time.sleep(0.5)
        return response.text

    @classmethod
    def _request_get_stream(cls, url, headers=None):
        if headers:
            cls.default_headers.update(headers)
        error_count = 0
        while True:
            try:
                response = requests.get(url, headers=cls.default_headers)
                if response.status_code != requests.codes.ok:
                    return None
                response.encoding = 'utf8'
                break
            except Exception as e:
                print(f'[LOG       ]| <function: {cls._request_get_stream.__name__}> {e}')
                error_count += 1
                if error_count > 100:
                    return None
                time.sleep(0.5)
        return response.content

    @classmethod
    def get_games_inventory(cls, page, platform=None, is_on_sale=False):
        """
            List all games price.
            :page:

            :is_on_sale:
                Default is None
                available
            :os:
                Default is None
                available input = ['win', 'mac', 'linux']
        """
        parameter = str()
        if platform and platform in [value for key, value in OS.__dict__.items() if not key.startswith('_')]:
            parameter = f'{parameter}&os={platform}'
        if is_on_sale is True:
            parameter = f'{parameter}&specials=1'
        url = f'{STEAM.SEARCH_DOMAIN}/search/?page={page}{parameter}'
        # SuperPrint(url, target_name='url')
        return cls._request_get_html(url=url)

    @classmethod
    def get_target_capsule(cls, target_id, is_bundle=False, token=None):
        """
            Get thumbnail
            :target_id: = app_id or bundle_id

            if target is bundle we need
            'bundle_id': '5879'
            :token: 'y8v8pu14quwe4xrv'
        """
        url = f'{STEAM.IMAGE_DOMAIN}/steam/apps/{target_id}/capsule_231x87.jpg'
        if is_bundle and token:
            url = f'{STEAM.IMAGE_DOMAIN}/steam/bundles/{target_id}/{token}/capsule_231x87.jpg'
        if is_bundle:
            url = f'{STEAM.IMAGE_DOMAIN}/steam/subs/{target_id}/capsule_231x87.jpg'
        stream = cls._request_get_stream(url=url)
        if not stream:
            return None
        return stream

    @classmethod
    def get_target_header(cls, target_id, is_bundle=False, token=None):
        """
            Get large image
            :target_id: = app_id or bundle_id

            if target is bundle we need
            'bundle_id': '5879'
            :token: 'y8v8pu14quwe4xrv'
        """
        url = f'{STEAM.IMAGE_DOMAIN}/steam/apps/{target_id}/header.jpg'
        if is_bundle and token:
            url = f'{STEAM.IMAGE_DOMAIN}/steam/bundles/{target_id}/{token}/header.jpg'
        if is_bundle:
            url = f'{STEAM.IMAGE_DOMAIN}/subs/{target_id}/header_586x192.jpg'
        stream = cls._request_get_stream(url=url)
        if not stream:
            return None
        return stream
