# built-in
import ast
import time
import threading
# submodule
from scraping_tools.super_print import SuperPrint
from scraping_tools.progress_bar import ProgressBar
from scraping_tools.snap_timer import SnapTimer
# project
from core.steam_api import SteamAPI
from core.beautiful_soup_handler import BSoupHandler
from core.steam_const import OS
from core.target_extractor import TargetExtractor


class SteamSpiderHandler:

    def __init__(self, is_on_sale, platform, filepath, countrol_number):
        self.is_on_sale = is_on_sale
        self.platform = platform
        self.filepath = filepath
        self.countrol_number = countrol_number
        self.info_container = dict()

        self.run()

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

    def get_search_results_amount(self, page_soup):
        """
            <div class="search_pagination_left">
                showing 1 - 25 of 2356
            </div>
        """
        search_pagination = self._get_pagination_container(page_soup=page_soup)
        amount_container = BSoupHandler.find_tag_by_key_value(
            soup=search_pagination, tag='div', key='class',
            value='search_pagination_left')
        string = BSoupHandler.get_text(soup=amount_container)
        result_amount = self._parse_targets_amount(string) if string else None
        SuperPrint(result_amount, 'result_amount')
        return result_amount

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
        SuperPrint(page_amount, 'page_amount')
        return page_amount

    def _slice_pages(self, last_page_number):
        all_pages_sliced = list()
        temp = list()
        for page in range(1, last_page_number+1):
            temp.append(page)
            if page % self.countrol_number == 0:
                pages = temp.copy()
                all_pages_sliced.append(pages)
                temp.clear()
        all_pages_sliced.append(pages)
        return all_pages_sliced

    @classmethod
    def _exec(cls, page, is_on_sale, platform, filepath, info_container):
        page_soup = cls._load_page(page, is_on_sale, platform)
        targets = cls._get_results_by_page(page_soup)
        for target in targets:
            info = TargetExtractor(target, filepath).get_info()
            if not info:
                continue
            target_id = info.get('id')
            info_container.update({target_id: info})

    def run(self):
        first_page = 1
        first_page_soup = self._load_page(first_page, self.is_on_sale, self.platform)
        pages_amount = self._get_search_pages_amount(first_page_soup)
        if pages_amount.isdigit():
            last_page_number = ast.literal_eval(pages_amount)
        else:
            raise('Cannot find last page number')
        all_pages_sliced = self._slice_pages(last_page_number)
        for pages_sliced in all_pages_sliced:
            threads = list()
            for page in pages_sliced:
                thr = threading.Thread(
                    target=self._exec,
                    args=(
                        page,
                        self.is_on_sale, self.platform,
                        self.filepath, self.info_container
                    )
                )
                thr.start()
                threads.append(thr)
            for thr in threads:
                thr.join(10)
        result = self.info_container
        print(result)

class SteamSpiderExcutor:

    def run(**kwargs):
        SteamSpiderHandler(**kwargs)
