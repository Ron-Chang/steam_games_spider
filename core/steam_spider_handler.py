# built-in
import time
import threading
# from urllib import parse
# submodule
from scraping_tools.super_print import SuperPrint
from scraping_tools.progress_bar import ProgressBar
from scraping_tools.snap_timer import SnapTimer
# project
from core.steam_api import SteamAPI
from core.beautiful_soup_handler import BSoupHandler
from core.steam_const import OS
from urllib import parse


class SteamSpiderHandler:
    print('BSoupHandler Import Succeed!')


class SteamSpiderExcutor:

    def run(is_on_sale=False, os=None):
        SteamAPI.get_games_inventory(page=1, is_on_sale=is_on_sale, os=os)
        print('SteamSpiderHandler Import Succeed!')
