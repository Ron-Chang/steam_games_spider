# built-in
import time
import requests
# submodule
from scraping_tools.super_print import SuperPrint
# project
from core.steam_const import OS, STEAM

class SteamAPI:

    @classmethod
    def _request_get(cls, url, headers=None):
        default_headers = {
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/79.0.3945.130 Safari/537.36'
            )
        }
        if headers:
            default_headers.update(headers)
        while True:
            try:
                response = requests.get(url, headers=default_headers)
                response.encoding = 'utf8'
                break
            except Exception as e:
                print(f'[LOG       ]| {e}')
                time.sleep(0.5)
        return response.text

    @classmethod
    def get_games_inventory(cls, page, os=None, is_on_sale=False):
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
        if os and os in [value for key, value in OS.__dict__.items() if not key.startswith('_')]:
            parameter  = f'{parameter}&os={os}'
        if is_on_sale is True:
            parameter  = f'{parameter}&specials=1'
        url = f'{STEAM.DOMAIN}?page={page}{parameter}'
        SuperPrint(url, target_name='url')
        return cls._request_get(url=url)



