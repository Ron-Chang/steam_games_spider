# built-in
import ast
import time
import threading
from datetime import datetime
# submodule
from scraping_tools.super_print import SuperPrint
from scraping_tools.progress_bar import ProgressBar
from scraping_tools.snap_timer import SnapTimer
from scraping_tools.utils import CommonUtils
# project
from app import db, spider_rs
from core.models import SteamGameInfo
from core.steam_api import SteamAPI
from core.data_parser import DataParser
from core.beautiful_soup_handler import BSoupHandler
from core.target_extractor import TargetExtractor


class SteamSpiderHandler:

    def __init__(self, is_on_sale, platform, filepath, control_number):
        self.is_on_sale = is_on_sale
        self.platform = platform
        self.filepath = filepath
        self.control_number = control_number
        self.info_container = dict()
        self.count = 0
        self.results_number = int()

        self.run()

    def _add_count(self):
        self.count += 1

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
            value='search_result_container')
        search_results = BSoupHandler.find_all_class(
            soup=search_result_container,
            class_name='search_result_row ds_collapse_flag')
        return search_results

    @staticmethod
    def _get_pagination_container(page_soup):
        """
             <div class="search_pagination">
        """
        search_pagination = BSoupHandler.find_tag_by_key_value(
            soup=page_soup, tag='div', key='class',
            value='search_pagination')
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
            value='search_pagination_left')
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
        page_amount = BSoupHandler.get_text(soup=pagination_soup)
        return page_amount

    def _slice_pages(self, last_page_number):
        all_pages_sliced = list()
        temp = list()
        pages = list()
        for page in range(1, last_page_number+1):
            temp.append(page)
            if page % self.control_number == 0:
                pages = temp.copy()
                all_pages_sliced.append(pages)
                temp.clear()
        if pages:
            all_pages_sliced.append(pages)
        return all_pages_sliced

    def _exec(self, page):
        page_soup = self._load_page(page, self.is_on_sale, self.platform)
        targets = self._get_results_by_page(page_soup)
        for target in targets:
            info = TargetExtractor(target, self.filepath).get()
            self._add_count()
            ProgressBar(count=self.count, amount=self.results_number)
            if not info:
                continue
            target_id = info.get('id')
            self.info_container.update({target_id: info})

    def run(self):
        first_page = 1
        first_page_soup = self._load_page(first_page, self.is_on_sale, self.platform)
        pages_amount = self._get_search_pages_amount(first_page_soup)
        SuperPrint(pages_amount, '[INFO      ]| pages_amount')
        results_amount = self._get_search_results_amount(first_page_soup)
        if pages_amount.isdigit() and results_amount.isdigit():
            last_page_number = ast.literal_eval(pages_amount)
            self.results_number = ast.literal_eval(results_amount)
        else:
            raise(Exception('Cannot find last page number'))

        all_pages_sliced = self._slice_pages(last_page_number)
        for pages_sliced in all_pages_sliced:
            threads = list()
            for page in pages_sliced:
                thr = threading.Thread(target=self._exec, args=(page,))
                thr.start()
                threads.append(thr)
            for thr in threads:
                thr.join(10)
        results = self.info_container
        # ################### TEST ####################
        with open('test/export.txt', 'w') as fw:
            fw.write('[\n')
            for result in results.values():
                fw.write(f'{str(result)},\n')
            fw.write('\n]')
        # ################### TEST ####################


class InserData:

    def update_database(**kwargs):
        """
            steam_id=1234567,
            title='test',
            discount=0.9,
            normal_price=120,
            overall_reviews='positive',
            released_date=datetime.now().date(),
            is_bundle=False,
            is_support_win=True,
            is_support_mac=False,
            is_support_linux=False,
            update_datetime=datetime.now(),
            create_datetime=datetime.now(),
        """
        steam_game_info = SteamGameInfo(**kwargs)
        db.session.add(steam_game_info)
        db.session.commit()


class SteamSpiderExecutor:

    @staticmethod
    @CommonUtils.snap_interval(hours=36)
    def run(snap_interval, **kwargs):
        while True:
            start = time.time()
            SteamSpiderHandler(**kwargs)
            SnapTimer(snap_interval=snap_interval, start=start)
