# built-in
import re

class DataParser:

    REGEX_BUNDLE_IMG_TOKEN = re.compile(r'.*\/\d+\/(.*)\/capsule.*')
    REGEX_OF_USERS_REVIEW = re.compile(r'.*<br>(\d+%)\ of\ the\ ([0-9,]+)\ user.*')
    REGEX_OF_RESULTS_AMOUNT = re.compile(r'.*of\ (\d+)')

    @classmethod
    def get_bundle_img_token(cls, input_string):
        """
            parse: ('https://steamcdn-a.akamaihd.net'
                '/steam/bundles/13278/1c3buxrordl3klbz'
                '/capsule_sm_120.jpg?t=1581020525')
            get: '1c3buxrordl3klbz'
        """
        token = cls.REGEX_BUNDLE_IMG_TOKEN.search(input_string)
        return token.group(1) if token else None

    @classmethod
    def get_results_amount(cls, input_string):
        """
        parse: ('showing 1 - 25 of 2356')
        get: '2356'
        """
        result = cls.REGEX_OF_RESULTS_AMOUNT.search(input_string)
        return result.group(1) if result else None

    @classmethod
    def get_users_review(cls, input_string):
        """
            parse: ('Mostly Positive<br>77% of the 638,504 user reviews '
                'for games in this bundle are positive.')
            get: 77%
            get: 638,504
        """
        result = cls.REGEX_OF_USERS_REVIEW.search(input_string)
        if not result:
            return None
        review_info = {
            'rate_of_positive': result.group(1),
            'amount_of_reviews': result.group(2)
        }
        return review_info


if __name__ == '__main__':
    print(f'[{"SAMPLE":^10}]')
    bundle_img_token = DataParser.get_bundle_img_token(
        'https://steamcdn-a.akamaihd.net'
        '/steam/bundles/13278/1c3buxrordl3klbz'
        '/capsule_sm_120.jpg?t=1581020525')
    results_amount = DataParser.get_results_amount('showing 1 - 25 of 2356')
    users_review = DataParser.get_users_review(
        'Mostly Positive<br>77% of the 638,504 user reviews '
        'for games in this bundle are positive.')
    print(bundle_img_token)
    print(results_amount)
    print(users_review)
