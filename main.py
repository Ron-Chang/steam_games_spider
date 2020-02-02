from scraping_tools.super_print import SuperPrint
from core.steam_spider_handler import SteamSpiderExcutor
from core.steam_const import OS

if __name__ == '__main__':
    test = SteamSpiderExcutor.run(is_on_sale=True, os=OS.WINDOWS)
    SuperPrint(test, target_name='test')
