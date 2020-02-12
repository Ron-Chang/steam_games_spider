from scraping_tools.super_print import SuperPrint
from core.steam_spider_handler import SteamSpiderExcutor
from core.steam_const import OS


if __name__ == '__main__':

    SETTING = {
        'is_on_sale': True,
        'platform': OS.WINDOWS,
        'filepath': 'img',
        'countrol_number': 15
    }

    test = SteamSpiderExcutor.run(**SETTING)

