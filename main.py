from core.steam_spider_handler import SteamSpiderExecutor
from core.steam_const import OS


if __name__ == '__main__':

    SETTING = {
        'is_on_sale': True,
        'platform': OS.WINDOWS,
        'filepath': 'img',
        'control_number': 15
    }

    test = SteamSpiderExecutor.run(**SETTING)

