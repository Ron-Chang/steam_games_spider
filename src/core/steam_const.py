

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

class OS:

    WINDOWS = 'win'
    MAC = 'mac'
    LINUX = 'linux'


# class HTML:

#     DECODE = {
#         "&amp;": "&",
#         "&quot;": '"',
#         "&apos;": "'",
#         "&gt;": ">",
#         "&lt;": "<",
#     }
