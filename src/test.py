import re
import os
from datetime import datetime
from io import BytesIO
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from PIL import Image
from core.steam_api import SteamAPI
from core.beautiful_soup_handler import BSoupHandler
from scraping_tools.super_print import SuperPrint

class Test:

    @staticmethod
    def request(page, is_on_sale, os):
        response = SteamAPI.get_games_inventory(
            page=page, is_on_sale=is_on_sale, os=os)
        response_soup = BSoupHandler.load_by_response(response=response)
        return response_soup

    @classmethod
    def get_search_results(cls, soup):
        """
            <div id="search_result_container">
        """
        search_result_container = BSoupHandler.find_tag_by_key_value(
            soup=soup, tag='div', key='id',
            value='search_result_container')
        search_results = BSoupHandler.find_all_class(
            soup=search_result_container,
            class_name='search_result_row ds_collapse_flag')
        return search_results

    @classmethod
    def _parse_token(cls, capsule_url):
        pattern = re.compile(r'.*\/\d+\/(.*)\/capsule.*')
        token = pattern.search(capsule_url)
        if not token:
            return None
        return token.group(1)

    @classmethod
    def _parse_review(cls, review_string):
        pattern = re.compile(r'.*<br>(\d+%)\ of\ the\ ([0-9,]+)\ user.*')
        result = pattern.search(review_string)
        review_info = dict()
        if not result:
            return None
        review_info.update({
            'rate_of_positive': result.group(1),
            'amount_of_reviews': result.group(2)
        })
        return review_info

    @classmethod
    def _parse_targets_amount(cls, amount_string):
        pattern = re.compile(r'.*of\ (\d+)')
        result = pattern.search(amount_string)
        if not result:
            return None
        return result.group(1)


    @classmethod
    def _get_bundle_token(cls, target_soup):
        """
          <img src="
            (
            https://steamcdn-a.akamaihd.net'
                '/steam/bundles/'
                '13278/1c3buxrordl3klbz'  # bundle_id/bundle_token
                '/capsule_sm_120.jpg?t=1581020525
            )
          ">
        """
        capsule_container = BSoupHandler.find_tag(
            soup=target_soup, tag_name='img')
        capsule_url = BSoupHandler.get_value_by_key(
            soup=capsule_container, key_name='src')
        return cls._parse_token(capsule_url=capsule_url)

    @classmethod
    def _get_target_metadata(cls, target_soup):
        target_id = BSoupHandler.get_value_by_key(
            soup=target_soup, key_name='data-ds-appid')
        is_bundle = False if target_id else True
        token = None if target_id else cls._get_bundle_token(
            target_soup=target_soup)
        target_metadata = {
            'target_id': target_id,
            'is_bundle': is_bundle,
            'token': token}
        if not target_id:
            target_id = BSoupHandler.get_value_by_key(
                soup=target_soup,
                key_name='data-ds-bundleid')
            target_metadata.update({'target_id': target_id})
        return target_metadata

    @classmethod
    def _get_target_capsule(cls, target_id, is_bundle, token, path):
        target_capsule = SteamAPI.get_target_capsule(
            target_id, is_bundle, token)
        if target_capsule is None:
            return None
        image_content = BytesIO(target_capsule)
        return Image.open(image_content)

    @classmethod
    def _get_target_header(cls, target_id, is_bundle, token, path):
        target_image = SteamAPI.get_target_header(
            target_id, is_bundle, token)
        if target_image is None:
            return None
        image_content = BytesIO(target_image)
        return Image.open(image_content)

    @classmethod
    def _get_target_discount(cls, target_soup):
        """
           <div class="col search_discount responsive_secondrow">
            <span>
             -10%
            </span>
           </div>
        """
        discount_container = BSoupHandler.find_tag_by_key_value(
            soup=target_soup,
            tag='div',
            key='class',
            value='col search_discount responsive_secondrow'
        )
        if discount_container is None:
            return None
        discount_span = BSoupHandler.find_tag(
            soup=discount_container, tag_name='span')
        return BSoupHandler.get_text(soup=discount_span)

    @classmethod
    def _get_target_released_date(cls, target_soup):
        """
        <div class="col search_released responsive_secondrow">
        13 Apr, 2015
        """
        released_data_container = BSoupHandler.find_tag_by_key_value(
            soup=target_soup, tag='div', key='class',
            value='col search_released responsive_secondrow'
        )
        released_data = BSoupHandler.get_text(soup=released_data_container)
        if not released_data:
            return None
        return datetime.strptime(released_data, '%d %b, %Y').date()

    @classmethod
    def _get_price_is_usual(cls, target_soup):
        """
           <div class="col search_price responsive_secondrow">
            NT$ 920
           </div>
        """
        price_container = BSoupHandler.find_tag_by_key_value(
            soup=target_soup, tag='div', key='class',
            value='col search_price responsive_secondrow'
        )
        price_text = BSoupHandler.get_text(soup=price_container)
        price = price_text.strip() if price_text else None
        return price

    @classmethod
    def _get_price_is_on_sale(cls, target_soup):
        """
            <div class="col search_price discounted responsive_secondrow">
              <span style="color: #888888;"><strike> NT$ 398 </strike></span><br/>NT$ 358
            </div>
        """
        price_container = BSoupHandler.find_tag_by_key_value(
            soup=target_soup, tag='div', key='class',
            value='col search_price discounted responsive_secondrow'
        )
        if not price_container:
            return None
        price_span = BSoupHandler.find_tag(soup=price_container, tag_name='span')
        price = BSoupHandler.get_text(soup=price_span)
        return price

    @classmethod
    def _get_target_price(cls, target_soup):
        try:
            price = cls._get_price_is_usual(target_soup=target_soup)
            if not price:
                return cls._get_price_is_on_sale(target_soup=target_soup)
            return price

        except Exception as e:
            SuperPrint(e)
            SuperPrint(target_soup)

    @classmethod
    def _get_target_title(cls, target_soup):
        """
         <span class="title">
             Grand Theft Auto V: Premium Online Edition
         </span>
        """
        title_container = BSoupHandler.find_tag_by_key_value(
            soup=target_soup, tag='span', key='class', value='title')
        return BSoupHandler.get_text(soup=title_container)

    @classmethod
    def _get_target_review(cls, target_soup):
        """
         <div class="col search_reviewscore responsive_secondrow">
            <span class="search_review_summary positive" data-tooltip-html="Mostly Positive&lt;br&gt;77% of the 638,504 user reviews for games in this bundle are positive.">
            </span>
        </div>
        """
        search_reviewscore_col = BSoupHandler.find_tag_by_key_value(
            soup=target_soup, tag='div', key='class',
            value='col search_reviewscore responsive_secondrow')
        if not search_reviewscore_col:
            return None
        summary_container = BSoupHandler.find_tag(
            soup=search_reviewscore_col, tag_name='span')

        if not summary_container:
            return None
        review_container = BSoupHandler.get_value_by_key(
            soup=summary_container, key_name='class')
        if not review_container:
            return  None
        overall_reviews = review_container[1]
        review_string = BSoupHandler.get_value_by_key(
            soup=summary_container,
            key_name='data-tooltip-html')
        review_info = cls._parse_review(review_string=review_string)
        review = {
            'overall_reviews': overall_reviews,
            'rate_of_positive': review_info['rate_of_positive'] if review_info else None,
            'amount_of_reviews': review_info['amount_of_reviews']  if review_info else None,
        }
        return review

    @classmethod
    def _get_target_platform(cls, target_soup):
        """
            <div class="col search_name ellipsis">
             <span class="title">
              Grand Theft Auto V: Premium Online Edition
             </span>
             <p>
              <span class="platform_img win">
              </span>
             </p>
            </div>
        """
        search_name_col = BSoupHandler.find_tag_by_key_value(
            soup=target_soup, tag='div', key='class',
            value='col search_name ellipsis')
        if not search_name_col:
            return None
        span_list = BSoupHandler.find_all_tag(
            soup=search_name_col, tag_name='span')
        if not span_list:
            return None
        platform_span_list = span_list[1:]
        platform_info = list()
        for platform_span in platform_span_list:
            platform = BSoupHandler.get_value_by_key(
                soup=platform_span ,key_name='class')
            if platform:
                platform_info.append(platform[1])
        return platform_info

    @classmethod
    def _download_image(cls, target_id, is_bundle, token, path):
        target_type = 'bundle' if is_bundle else 'app'

        target_capsule = cls._get_target_capsule(
            target_id=target_id, is_bundle=is_bundle, token=token, path=path)
        if target_capsule:
            filename = f'steam_{target_type}_{target_id}_capsule.jpg'
            filepath = os.path.join(path, filename)
            target_capsule.save(filepath)

        target_header = cls._get_target_header(
            target_id=target_id, is_bundle=is_bundle, token=token, path=path)
        if target_header:
            filename = f'steam_{target_type}_{target_id}_header.jpg'
            filepath = os.path.join(path, filename)
            target_header.save(filepath)

    @classmethod
    def get_target_info(cls, target_soup):
        """
            <a
                class="search_result_row ds_collapse_flag"
                data-ds-appid="582010"
                data-ds-crtrids="[33273264,34827959]"
                data-ds-itemkey="App_582010"
                data-ds-tagids="[1685,3859,19,1695,122,1697,21]"
                data-search-page="1"
                href="https://store.steampowered.com/app/582010/MONSTER_HUNTER_WORLD/?snr=1_7_7_230_150_1"
                onmouseout="HideGameHover( this, event, 'global_hover' )"
                onmouseover="
                    GameHover(
                        this,
                        event,
                        'global_hover',
                        {&quot;type&quot;:&quot;app&quot;,&quot;id&quot;:582010,&quot;public&quot;:1,&quot;v6&quot;:1}
                    );
                "
            >
        """
        target_metadata = cls._get_target_metadata(target_soup=target_soup)
        target_id = target_metadata['target_id']
        is_bundle = target_metadata['is_bundle']
        token = target_metadata['token']

        if not target_id:
            SuperPrint(BSoupHandler.print(target_soup))
            return None
        cls._download_image(
            target_id=target_id, is_bundle=is_bundle,
            token=token, path='img')

        title = cls._get_target_title(target_soup=target_soup)
        platform = cls._get_target_platform(target_soup=target_soup)
        discount = cls._get_target_discount(target_soup=target_soup)
        normal_price = cls._get_target_price(target_soup=target_soup)
        released_data = cls._get_target_released_date(target_soup=target_soup)
        review = cls._get_target_review(target_soup=target_soup)

        target_info = {
            'id': target_id,
            'title': title,
            'platform': platform,
            'discount': discount,
            'normal_price': normal_price,
            'released_data': released_data,
            'review': review,
        }
        return target_info

    @staticmethod
    def _get_pagination_container(page_soup):
        """
             <div class="search_pagination">
        """
        search_pagination = BSoupHandler.find_tag_by_key_value(
            soup=page_soup, tag='div', key='class',
            value='search_pagination')
        return search_pagination

    @classmethod
    def get_search_results_amount(cls, page_soup):
        """
            <div class="search_pagination_left">
                showing 1 - 25 of 2356
            </div>
        """
        search_pagination = cls._get_pagination_container(page_soup=page_soup)
        amount_container = BSoupHandler.find_tag_by_key_value(
            soup=search_pagination, tag='div', key='class',
            value='search_pagination_left')
        string = BSoupHandler.get_text(soup=amount_container)
        result_amount = cls._parse_targets_amount(string) if string else None
        SuperPrint(result_amount, 'result_amount')
        return result_amount

    @classmethod
    def get_search_pages_amount(cls, page_soup):
        """
            <a class="pagebtn" href="a_link"> < </a>
            <a href="a_link"> 2 </a>
            <a href="a_link"> 3 </a>
                ...
            <a href="a_link"> 95 </a>
            <a class="pagebtn" href="a_link"> > </a>
        """
        search_pagination = cls._get_pagination_container(page_soup=page_soup)
        pagination_list = BSoupHandler.find_all_tag(
            soup=search_pagination, tag_name='a')
        pagination_soup = pagination_list[-2] if pagination_list else None
        page_amount = BSoupHandler.get_text(soup=pagination_soup)
        SuperPrint(page_amount, 'page_amount')
        return page_amount


if __name__ == '__main__':

    page_soup = Test.request(page=8, is_on_sale=True, os=None)
    search_results = Test.get_search_results_amount(page_soup=page_soup)
    search_results = Test.get_search_pages_amount(page_soup=page_soup)
    # search_results = Test.get_search_results(soup=page_soup)
    # for target_soup in search_results:
    #     target_info = Test.get_target_info(target_soup=target_soup)
    #     SuperPrint(target_info)
