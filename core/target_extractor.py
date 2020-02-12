# built-in
from datetime import datetime
# project
from core.data_parser import DataParser
from core.beautiful_soup_handler import BSoupHandler
from core.image_handler import ImageHandler


class TargetExtractor:

    def __init__(self, target_soup, filepath):
        self.target_soup = target_soup
        self.filepath = filepath

        self.target_info = self._extract_target()

    def _get_metadata(self):
        """
            <a class="search_result_row ds_collapse_flag"
            data-ds-appid="582010"
            data-ds-crtrids="[33273264,34827959]"
            data-ds-itemkey="App_582010"
            data-ds-tagids="[1685,3859,19,1695,122,1697,21]"
            >
        """
        app_id = BSoupHandler.get_value_by_key(
            soup=self.target_soup, key_name='data-ds-appid')
        bundle_id = BSoupHandler.get_value_by_key(
                soup=self.target_soup, key_name='data-ds-bundleid')
        if app_id:
            return {'target_id': app_id, 'is_bundle': False, 'token': None}
        if bundle_id:
            capsule_container = BSoupHandler.find_tag(
                soup=self.target_soup, tag_name='img')
            capsule_url = BSoupHandler.get_value_by_key(
                soup=capsule_container, key_name='src')
            token = DataParser.get_bundle_img_token(capsule_url)
            return {'target_id': bundle_id, 'is_bundle': True, 'token': token}
        return {'target_id': None, 'is_bundle': False, 'token': None}

    def _get_title(self):
        """
         <span class="title">
             Grand Theft Auto V: Premium Online Edition
         </span>
        """
        title_container = BSoupHandler.find_tag_by_key_value(
            soup=self.target_soup, tag='span', key='class', value='title')
        return BSoupHandler.get_text(soup=title_container)

    def _get_platform(self):
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
                soup=platform_span, key_name='class')
            if platform:
                if len(platform) == 1:
                    platform_info.append(platform)
                else:
                    platform_info.append(platform[1])
        return platform_info

    def _get_review(self):
        """
         <div class="col search_reviewscore responsive_secondrow">
            <span class=
                    "search_review_summary positive"
                data-tooltip-html=
                    "Mostly Positive&lt;br&gt;77% of the 638,504 user reviews for games in this bundle are positive.">
            </span>
        </div>
        """
        search_reviewscore_col = BSoupHandler.find_tag_by_key_value(
            soup=self.target_soup, tag='div', key='class',
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
            return None
        overall_reviews = review_container[1]
        review_string = BSoupHandler.get_value_by_key(
            soup=summary_container,
            key_name='data-tooltip-html')
        review_info = DataParser.get_users_review(input_string=review_string)
        review = {
            'overall_reviews': overall_reviews,
            'rate_of_positive': review_info['rate_of_positive'] if review_info else None,
            'amount_of_reviews': review_info['amount_of_reviews'] if review_info else None,
        }
        return review

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
        return BSoupHandler.get_text(soup=discount_span)

    def _get_released_date(self):
        """
        <div class="col search_released responsive_secondrow">
        13 Apr, 2015
        """
        released_data_container = BSoupHandler.find_tag_by_key_value(
            soup=self.target_soup, tag='div', key='class',
            value='col search_released responsive_secondrow')
        released_data = BSoupHandler.get_text(soup=released_data_container)
        if not released_data:
            return None
        if released_data.isdigit() and len(released_data) == 4:
            return datetime.strptime(released_data, '%Y').date()
        elif len(released_data.split(' ')) == 2:
            try:
                return datetime.strptime(released_data, '%b %Y').date()
            except Exception as e:
                print(f'[LOG       ]| <function: {self._get_released_date.__name__}> {e}')
                return None
        return datetime.strptime(released_data, '%d %b, %Y').date()

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
        return price_text.strip() if price_text else None

    def _extract_target(self):
        metadata = self._get_metadata()
        target_id = metadata.get('target_id')
        if not target_id:
            return None
        is_bundle = metadata.get('is_bundle')
        token = metadata.get('token')
        ImageHandler.download_image(
            target_id, is_bundle, token, self.filepath)
        target_info = {
            'id': target_id,
            'title': self._get_title(),
            'is_bundle': is_bundle,
            'platform': self._get_platform(),
            'discount': self._get_discount(),
            'normal_price': self._get_price(),
            'released_date': self._get_released_date(),
            'review': self._get_review()
        }
        return target_info

    def get(self):
        return self.target_info
