# built-in
import ast
from datetime import datetime
# project
from core.data_parser import DataParser
from core.beautiful_soup_handler import BSoupHandler
from core.image_handler import ImageHandler
from scraping_tools.super_print import SuperPrint
from scraping_tools.log_stash import LogStash
from core.steam_const import OS, STEAM


class TargetExtractor:

    def __init__(self, target_soup, filepath):
        self.target_soup = target_soup
        self.filepath = filepath

        self.target_info = self._extract_target()

    def _get_token(self):
        capsule_container = BSoupHandler.find_tag(
            soup=self.target_soup, tag_name='img')
        capsule_url = BSoupHandler.get_value_by_key(
            soup=capsule_container, key_name='src')
        token = DataParser.get_bundle_img_token(capsule_url)
        return token

    def _get_metadata(self):
        """
            <a class="search_result_row ds_collapse_flag"
            data-ds-appid="582010"
            data-ds-crtrids="[33273264,34827959]"
            data-ds-itemkey="App_582010"
            data-ds-tagids="[1685,3859,19,1695,122,1697,21]"
            >

            condition: data-ds-appid="215770,215772"

            appid = target_id.split(',')

            def _is_digit():
                for appid in appid_list():
                    if not appid.isdigit():
                        return False
                return True

            if len(appid)>1 and cls._is_digit(appid):
                return data-ds-packageid

            data-ds-packageid="16492"  data-ds-itemkey="Sub_16492"
            data-ds-packageid

        """
        app_id = BSoupHandler.get_value_by_key(
            soup=self.target_soup, key_name=STEAM.LABEL.APP_ID)
        bundle_id = BSoupHandler.get_value_by_key(
                soup=self.target_soup, key_name=STEAM.LABEL.BUNDLE_ID)
        package_id = BSoupHandler.get_value_by_key(
                soup=self.target_soup, key_name=STEAM.LABEL.PACKAGE_ID)
        if package_id:
            return {'target_id': package_id, 'is_bundle': True, 'token': None}
        if bundle_id:
            token = self._get_token()
            return {'target_id': bundle_id, 'is_bundle': True, 'token': token}
        return {'target_id': app_id, 'is_bundle': False, 'token': None}

    def _get_title(self):
        """
         <span class="title">
             Grand Theft Auto V: Premium Online Edition
         </span>
        """
        title_container = BSoupHandler.find_tag_by_key_value(
            soup=self.target_soup, tag='span', key='class', value='title')
        return BSoupHandler.get_text(soup=title_container)

    def _get_platforms(self):
        """
            <div class="col search_name ellipsis">
             <span class="title">
              THE GAME TITLE
             </span>
             <p>
              <span class="platform_img win">
              <span class="platform_img mac">
              <span class="platform_img linux">
              </span>
             </p>
            </div>
        """
        search_name_col = BSoupHandler.find_tag_by_key_value(
            soup=self.target_soup, tag='div', key='class',
            value=STEAM.LABEL.CONTAINER_OF_PLATFORM)
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
                soup=platform_span, key_name='class')
            if platform:
                if len(platform) == 1:
                    platform_info.append(platform)
                else:
                    platform_info.append(platform[1])
        return platform_info

    @staticmethod
    def _convert_decimal(rate):
        text = rate.strip('-').strip('%')
        if not text:
            return None
        try:
            number = ast.literal_eval(text)
        except:
            return None

        if not isinstance(number, int):
            return None
        return round(number * 0.01, 2)

    @staticmethod
    def _convert_integer(num):
        text = num.replace(',', '')
        if not text:
            return None
        try:
            number = ast.literal_eval(text)
        except:
            return None

        if not isinstance(number, int):
            return None
        return number

    def _get_reviews(self):
        """
         <div class="col search_reviewscore responsive_secondrow">
            <span class=
                    "search_review_summary positive"
                data-tooltip-html=
                    "Mostly Positive&lt;br&gt;77% of the 638,504 user reviews for games in this bundle are positive.">
            </span>
        </div>
        """
        reviews = dict()
        search_reviewscore_col = BSoupHandler.find_tag_by_key_value(
            soup=self.target_soup, tag='div', key='class',
            value=STEAM.LABEL.CONTAINER_OF_REVIEW)
        if not search_reviewscore_col:
            return reviews
        summary_container = BSoupHandler.find_tag(
            soup=search_reviewscore_col, tag_name='span')
        if not summary_container:
            return reviews
        review_string = BSoupHandler.get_value_by_key(
            soup=summary_container,
            key_name=STEAM.LABEL.RESULTS_OF_REVIEW)
        review_info = DataParser.get_users_review(input_string=review_string)

        rate = review_info.get('rate_of_positive')
        rate_of_positive = self._convert_decimal(rate) if rate else None

        amount = review_info.get('amount_of_reviews')
        amount_of_reviews = self._convert_integer(amount) if amount else None
        reviews.update({
            'rate_of_positive': rate_of_positive,
            'amount_of_reviews': amount_of_reviews
        })
        return reviews

    def _get_discount(self):
        """
            <div class="col search_discount responsive_secondrow">
                <span>-10%</span>
            </div>
        """
        discount_container = BSoupHandler.find_tag_by_key_value(
            soup=self.target_soup,
            tag='div',
            key='class',
            value='col search_discount responsive_secondrow'
        )
        if discount_container is None:
            return None
        discount_span = BSoupHandler.find_tag(
            soup=discount_container, tag_name='span')
        rate = BSoupHandler.get_text(soup=discount_span)
        discount = self._convert_decimal(rate) if rate else None
        return 1 - discount if discount else None

    def _get_released_date(self):
        """
        <div class="col search_released responsive_secondrow">
        13 Apr, 2015
        """
        released_date_container = BSoupHandler.find_tag_by_key_value(
            soup=self.target_soup, tag='div', key='class',
            value='col search_released responsive_secondrow')
        released_date = BSoupHandler.get_text(soup=released_date_container)
        if not released_date:
            return None
        LogStash.debug(msg=f'released_date: {released_date}')
        released_date_list = released_date.split(' ')
        try:
            if released_date_list == 3 and released_date_list[0].isdigit():
                return datetime.strptime(released_date, '%d %b, %Y').date()
            elif released_date_list == 3 and released_date_list[1].isdigit():
                return datetime.strptime(released_date, '%b %d, %Y').date()
            elif released_date_list == 2 and released_date_list[0].isdigit():
                return datetime.strptime(released_date, '%Y %b').date()
            elif released_date_list == 2 and released_date_list[1].isdigit():
                return datetime.strptime(released_date, '%b %Y').date()
            elif released_date_list == 1:
                return datetime.strptime(released_date, '%Y').date()
            else:
                return None
        except ValueError:
            LogStash.info(msg=released_date)
        except Exception as e:
            LogStash.error(msg=f'{e}|{released_date}')


    def _get_price(self):
        """
            <div class="col search_price responsive_secondrow">
                NT$ 920
            </div>
            -----------------------------------------------------------------
            <div class="col search_price discounted responsive_secondrow">
                <span style="color: #888888;"><strike> NT$ 398 </strike></span><br/>NT$ 358
            </div>
        """
        price_container = BSoupHandler.find_tag_by_key_value(
            soup=self.target_soup, tag='div', key='class',
            value='col search_price responsive_secondrow')
        special_price_container = BSoupHandler.find_tag_by_key_value(
            soup=self.target_soup, tag='div', key='class',
            value='col search_price discounted responsive_secondrow')
        if price_container:
            price_text = BSoupHandler.get_text(soup=price_container)
        elif special_price_container:
            price_span = BSoupHandler.find_tag(
                soup=special_price_container, tag_name='span')
            price_text = BSoupHandler.get_text(soup=price_span)
        else:
            price_text = None
        return price_text.strip().replace(',', '') if price_text else None

    def _extract_target(self):
        metadata = self._get_metadata()
        target_id = metadata.get('target_id')
        if not target_id:
            LogStash.error(msg=f'metadata: {metadata}')
            return None
        is_bundle = metadata.get('is_bundle')
        token = metadata.get('token')
        ImageHandler.download_image(
            target_id, is_bundle, token, self.filepath)

        title = self._get_title()
        platforms = self._get_platforms()
        discount = self._get_discount()
        price = self._get_price()
        reviews = self._get_reviews()
        rate_of_positive = reviews.get('rate_of_positive')
        amount_of_reviews = reviews.get('amount_of_reviews')
        rank_of_review = None
        if rate_of_positive and amount_of_reviews:
            rank_of_review = STEAM.REVIEWS.get_rank(**reviews)
        released_date = self._get_released_date()
        target_info = {
            'steam_id': target_id,
            'title': title,
            'is_bundle': is_bundle,
            'is_supported_win': True if OS.WINDOWS in platforms else False,
            'is_supported_mac': True if OS.MAC in platforms else False,
            'is_supported_linux': True if OS.LINUX in platforms else False,
            'discount': discount,
            'normal_price': price,
            'released_date': released_date,
            'rank_of_review': rank_of_review,
            'rate_of_positive': rate_of_positive,
            'amount_of_reviews': amount_of_reviews,
        }
        return target_info

    def get(self):
        return self.target_info
