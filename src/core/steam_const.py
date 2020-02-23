

class OS:
    WINDOWS = 'win'
    MAC = 'mac'
    LINUX = 'linux'


class STEAM:
    SEARCH_DOMAIN = 'https://store.steampowered.com'
    IMAGE_DOMAIN = 'https://steamcdn-a.akamaihd.net'

    class LABEL:

        CONTAINER_OF_APPS = 'search_result_row ds_collapse_flag'
        CONTAINER_OF_PAGINATION = 'search_pagination'
        CONTAINER_OF_PLATFORM = 'col search_name ellipsis'
        CONTAINER_OF_REVIEW = 'col search_reviewscore responsive_secondrow'
        CONTAINER_OF_SEARCH_RESULT = 'search_result_container'

        AMOUNT_OF_RESULTS = 'search_pagination_left'
        RESULTS_OF_REVIEW = 'data-tooltip-html'

        APP_ID = 'data-ds-appid'
        BUNDLE_ID = 'data-ds-bundleid'
        PACKAGE_ID = 'data-ds-packageid'

    label = "data-ds-appid"

    class REVIEWS:

        RANK_INFO = {
            '9': 'Overwhelmingly Positive',
            '8': 'Very Positive',
            '7': 'Positive',
            '6': 'Mostly Positive',
            '5': 'Mixed',
            '4': 'Mostly Negative',
            '3': 'Negative',
            '2': 'Very Negative',
            '1': 'Overwhelmingly Negative',
        }

        @staticmethod
        def get_rank(rate_of_positive, amount_of_reviews):
            if rate_of_positive >= 0.95 and amount_of_reviews >= 500:
                return 9
            elif rate_of_positive >= 0.8 and amount_of_reviews >= 50:
                return 8
            elif rate_of_positive >= 0.8 and 50 > amount_of_reviews:
                return 7
            elif 0.8 > rate_of_positive >= 0.7:
                return 6
            elif 0.7 > rate_of_positive >= 0.4:
                return 5
            elif 0.4 > rate_of_positive >= 0.2:
                return 4
            elif 0.2 > rate_of_positive and 50 > amount_of_reviews:
                return 3
            elif 0.2 > rate_of_positive and 500 > amount_of_reviews >= 50:
                return 2
            elif 0.2 > rate_of_positive and amount_of_reviews >= 500:
                return 1

        @classmethod
        def get_rank_description(cls, rank):
            return cls.RANK_INFO.get(str(rank))
