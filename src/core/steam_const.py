

class STEAM:
    SEARCH_DOMAIN = 'https://store.steampowered.com'
    IMAGE_DOMAIN = 'https://steamcdn-a.akamaihd.net'

    APPS_CONTAINER = "search_result_row ds_collapse_flag"
    label = "data-ds-appid"

    OVERALL_REVIEW = {
        'positive': 1,
        'mixed': 0,
        'negative': -1,
    }

    class REVIEWS:

        RANK = {
            'Overwhelmingly Positive': 4,
            'Very Positive': 3,
            'Positive': 2,
            'Mostly Positive': 1,
            'Mixed': 0,
            'Mostly Negative': -1,
            'Negative': -2,
            'Very Negative': -3,
            'Overwhelmingly Negative': -4,
        }

        @staticmethod
        def get_overall_review(rate_of_positive, reviews_amount):
            if rate_of_positive >= 95 and reviews_amount >= 500:
                return 'Overwhelmingly Positive'
            elif rate_of_positive >= 80 and 500 > reviews_amount >= 50:
                return 'Very Positive'
            elif rate_of_positive >= 80 and 50 > reviews_amount:
                return 'Positive'
            elif 80 > rate_of_positive >= 70:
                return 'Mostly Positive'
            elif 70 > rate_of_positive >= 40:
                return 'Mixed'
            elif 40 > rate_of_positive >= 20:
                return 'Mostly Negative'
            elif rate_of_positive > 20 and 50 > reviews_amount:
                return 'Negative'
            elif rate_of_positive > 20 and 500 > reviews_amount >= 50:
                return 'Very Negative'
            elif rate_of_positive > 20 and reviews_amount >= 500:
                return 'Overwhelmingly Negative'

        @classmethod
        def get_rank(overall_review):
            return cls.RANK.get(overall_review)


class OS:

    WINDOWS = 'win'
    MAC = 'mac'
    LINUX = 'linux'
