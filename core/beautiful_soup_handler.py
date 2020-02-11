import os
from bs4 import BeautifulSoup

class BSoupHandler:

    @staticmethod
    def load_by_response(response):
        return BeautifulSoup(response, 'html.parser')

    @staticmethod
    def find_img(soup):
        return soup.find('img').get('src')

    @staticmethod
    def find_href(soup):
        return soup.find('a').get('href')

    @staticmethod
    def find_class(soup, class_name):
        return soup.find(class_=class_name)

    @staticmethod
    def find_all_class(soup, class_name):
        return soup.find_all(class_=class_name)

    @staticmethod
    def find_tag(soup, tag_name):
        return soup.find(tag_name)

    @staticmethod
    def find_all_tag(soup, tag_name):
        return soup.find_all(tag_name)

    @staticmethod
    def find_tag_by_key_value(soup, tag, key, value):
        """find <div> tag and <class> value is "body"
                <div class="body" itemprop="articleBody">   string </div>
                <tag key=value itemprop="articleBody">      string </tag>
        """
        return soup.find(tag, {key: value})

    @staticmethod
    def find_all_tag_by_key_value(soup, tag, key, value):
        """find <div> tag and <class> value is "body"
                <div class="body" itemprop="articleBody">   string </div>
                <tag key=value itemprop="articleBody">      string </tag>
        """
        return soup.find_all(tag, {key: value})

    @staticmethod
    def get_value_by_key(soup, key_name):
        return soup.get(key_name)

    @staticmethod
    def get_text(soup):
        string = None if soup is None else soup.get_text()
        return None if string is None else string.strip()

    @staticmethod
    def print(soup):

        def get_console_width():
            try:
                return os.get_terminal_size(0)[0]
            except:
                return 76

        def print_divider():
            console_width = get_console_width()
            print('=' * console_width)

        if soup:
            print_divider()
            print(f'{" : START PRINT : "}')
            print_divider()
            print(soup.prettify())
            print_divider()
            print(f'{" : END PRINT : "}')
            print_divider()
