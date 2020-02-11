# built-in
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
from core.target_handler import TargetHandler
from urllib import parse


class SteamSpiderHandler:

    def __init__(self, is_on_sale, platform):
        self.is_on_sale = is_on_sale
        self.platform = platform

    ############## START: static method ##############

    @staticmethod
    def _load_page(page, is_on_sale, platform):
        """
            load single page as soup obj
        """
        response = SteamAPI.get_games_inventory(
            page=page, is_on_sale=is_on_sale, platform=platform)
        return BSoupHandler.load_by_response(response=response)

    # @staticmethod
    # def _is_empty_page(search_result_container):
    #     text = BSoupHandler.get_text(soup=search_result_container)
    #     text_parsed = search_result_text.strip()
    #     if 'No results were returned for that query.' == text_parsed:
    #         return True
    #     return False

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


    ############## END: static method ##############
    ############## START: collect targets and pages number ##############

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

    def get_search_pages_amount(self, page_soup):
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

    ############## END: collect targets and pages number ##############


    # @staticmethod
    # def _get_response(page, is_on_sale, os):
    #     response = SteamAPI.get_games_inventory(
    #         page=page, is_on_sale=is_on_sale, os=os)
    #     return response

    # @staticmethod
    # def _get_search_result_container(response):
    #     soup = BSoupHandler.load_by_response(response)
    #     search_result_container = BSoupHandler.find_tag_by_key_value(
    #         soup=soup,
    #         tag='div',
    #         key='id',
    #         value='search_result_container'
    #     )
    #     return search_result_container

    # @staticmethod
    # def _get_response(page, is_on_sale, os):
    #     response = SteamAPI.get_games_inventory(
    #         page=page, is_on_sale=is_on_sale, os=os)
    #     response_soup = BSoupHandler.load_by_response(response=response)
    #     return response_soup

    # @classmethod
    # def _exec(cls, search_result, container):
    #     target_info = TargetHandler.get_target_info(search_result)
    #     SuperPrint(target_info, 'target_info')

    def run(self):
        page = 1
        page_soup = self._load_page(page, self.is_on_sale, self.platform)
        pages_amount = self.get_search_pages_amount(page_soup)
        targets = self._get_results_by_page(page_soup)
        for target in targets:
            info = TargetHandler(target, 'img').get_target_info()
            print(info)
        # container = list()
        # while True:
        #     response = cls._get_response(page=page, is_on_sale=is_on_sale, os=os)
        #     search_result = cls._get_search_result_container(response)
        #     if cls._is_empty_page(search_result=search_result):
        #         SuperPrint(f'"Page.{page}" is the last page of the query.')
        #         break
        #     cls._exec(search_result=search_result, container=container)
        #     page += 1


class SteamSpiderExcutor:

    def run(is_on_sale=False, platform=None):
        SteamSpiderHandler(is_on_sale=is_on_sale, platform=platform).run()
