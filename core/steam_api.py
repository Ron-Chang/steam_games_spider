# built-in
import time
import requests
# submodule
from scraping_tools.super_print import SuperPrint
# project
from core.steam_const import OS

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
        url = f'https://store.steampowered.com/search/?page={page}'
        os_list = [value for key, value in OS.__dict__.items() if not key.startswith('_')]
        if os and os in os_list:
            url  = f'{url}&os={os}'
        if is_on_sale is True:
            url  = f'{url}&specials=1'

        SuperPrint(url, target_name='url')
        return cls._request_get(url=url)



