# built-in
import ast
import time
import threading
from datetime import datetime
# submodule
from common.models import SteamGameInfo
from scraping_tools.super_print import SuperPrint
from scraping_tools.progress_bar import ProgressBar
from scraping_tools.snap_timer import SnapTimer
from scraping_tools.utils import DecoratorUtils
# project
from app import db, spider_rs
from core.steam_api import SteamAPI
from core.steam_const import STEAM
from core.data_parser import DataParser
from core.beautiful_soup_handler import BSoupHandler
from core.target_extractor import TargetExtractor


class SteamSpiderHandler:

    def __init__(self, is_on_sale, platform, filepath, slice_num):
        self.is_on_sale = is_on_sale
        self.platform = platform
        self.filepath = filepath
        self.slice_num = slice_num
        self.amount = int()
        self.count = 0

        self.insert_amount = 0
        self.update_amount = 0

        self.run()

    def _add_count(self):
        self.count += 1

    def _add_insert_amount(self):
        self.insert_amount += 1

    def _add_update_amount(self):
        self.update_amount += 1

    @staticmethod
    def _load_page(page, is_on_sale, platform):
        """
            load single page as soup obj
        """
        response = SteamAPI.get_games_inventory(
            page=page, is_on_sale=is_on_sale, platform=platform)
        return BSoupHandler.load_by_response(response=response)

    @staticmethod
    def _get_results_by_page(page_soup):
        """
            <div id="search_result_container">
        """
        search_result_container = BSoupHandler.find_tag_by_key_value(
            soup=page_soup, tag='div', key='id',
            value=STEAM.LABEL.CONTAINER_OF_SEARCH_RESULT)
        search_results = BSoupHandler.find_all_class(
            soup=search_result_container,
            class_name=STEAM.LABEL.CONTAINER_OF_APPS)
        return search_results

    @staticmethod
    def _get_pagination_container(page_soup):
        """
             <div class="search_pagination">
        """
        search_pagination = BSoupHandler.find_tag_by_key_value(
            soup=page_soup, tag='div', key='class',
            value=STEAM.LABEL.CONTAINER_OF_PAGINATION)
        return search_pagination

    def _get_search_results_amount(self, page_soup):
        """
            <div class="search_pagination_left">
                showing 1 - 25 of 2356
            </div>
        """
        search_pagination = self._get_pagination_container(page_soup=page_soup)
        amount_container = BSoupHandler.find_tag_by_key_value(
            soup=search_pagination, tag='div', key='class',
            value=STEAM.LABEL.AMOUNT_OF_RESULTS)
        amount_string = BSoupHandler.get_text(soup=amount_container)
        return DataParser.get_results_amount(amount_string) if amount_string else None

    def _get_search_pages_amount(self, page_soup):
        """
            <a class="pagebtn" href="a_link"> < </a>
            <a href="a_link"> 2 </a>
            <a href="a_link"> 3 </a>
                ...
            <a href="a_link"> 95 </a>
            <a class="pagebtn" href="a_link"> > </a>
        """
        search_pagination = self._get_pagination_container(page_soup=page_soup)
        pagination_list = BSoupHandler.find_all_tag(
            soup=search_pagination, tag_name='a')
        pagination_soup = pagination_list[-2] if pagination_list else None
        return BSoupHandler.get_text(soup=pagination_soup)

    def _get_slice_page_container(self, page_amount):
        slice_page_container = list()
        temp = list()
        for page in range(1, page_amount+1):
            temp.append(page)
            if page % self.slice_num == 0:
                slice_page_container.append(temp.copy())
                temp.clear()
        if temp:
            slice_page_container.append(temp)
        return slice_page_container

    def _updata_data(self, model, **kwargs):
        self._add_update_amount()
        for key, value in kwargs.items():
            setattr(model, key, value)

    def _insert_data(self, **kwargs):
        self._add_insert_amount()
        steam_game_info = SteamGameInfo(**kwargs)
        db.session.add(steam_game_info)

    def _exec(self, page, result_container):
        page_soup = self._load_page(page, self.is_on_sale, self.platform)
        targets = self._get_results_by_page(page_soup)
        for target in targets:
            info = TargetExtractor(target, self.filepath).get()
            self._add_count()
            ProgressBar(count=self.count, amount=self.amount)
            if not info:
                continue
            result_container.append(info)

    def run(self):
        first_page = 1
        first_page_soup = self._load_page(first_page, self.is_on_sale, self.platform)
        pages_amount = self._get_search_pages_amount(first_page_soup)

        SuperPrint(pages_amount, '[INFO      ]| pages_amount')
        print(f'[INFO      ]| is_on_sale: {self.is_on_sale}')
        print(f'[INFO      ]| platform: {self.platform}')
        print(f'[INFO      ]| filepath: {self.filepath}')
        print(f'[INFO      ]| slice_num: {self.slice_num}')

        results_amount = self._get_search_results_amount(first_page_soup)
        if pages_amount.isdigit() and results_amount.isdigit():
            page_amount = ast.literal_eval(pages_amount)
            self.amount = ast.literal_eval(results_amount)
        else:
            raise(Exception('Cannot find last page number'))

        all_pages_sliced = self._get_slice_page_container(page_amount)
        for pages_sliced in all_pages_sliced:
            threads = list()
            result_container = list()
            for page in pages_sliced:
                thr = threading.Thread(
                    target=self._exec,
                    args=(page, result_container))
                thr.start()
                threads.append(thr)
            for thr in threads:
                thr.join(10)

            for result in result_container:
                steam_id = result.get('steam_id')
                title = result.get('title')
                # SuperPrint(title, steam_id)
                game = SteamGameInfo.query.filter_by(steam_id=steam_id).first()
                try:
                    if game:
                        self._updata_data(game, **result)
                    else:
                        self._insert_data(**result)
                    db.session.commit()
                except Exception as e:
                    SuperPrint(f'Error: {e} | {result}')
                    continue

    def get_update_amount(self):
        return self.update_amount

    def get_insert_amount(self):
        return self.insert_amount


class SteamSpiderExecutor:

    @staticmethod
    @DecoratorUtils.snap_interval(hours=36)
    def run(snap_interval, **kwargs):
        while True:
            start = time.time()
            steam = SteamSpiderHandler(**kwargs)
            extra_info = {
                'upd. qty': steam.get_update_amount(),
                'ins. qty': steam.get_insert_amount()
            }
            SnapTimer(snap_interval=snap_interval, start=start, **extra_info)
