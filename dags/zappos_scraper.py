import logging
import requests

from lxml import html

from sqlite_db import SqliteDB

"""
ZapposScraper holds methods and properties that required to scrape shoe data from https://www.zappos.com.
Most of the XPATHS won't change frequently, therefore hardcoded.

Made it into a class to categorize all methods for ZapposScraper into one place.
"""


# Note: currently only one page with 100 products is scraping for demo purpose.

class ZapposScraper:
    def __init__(self):
        self.URL = 'https://www.zappos.com'
        self.MEN_CATEGORY = '/html/body/div[1]/div[1]/header/div[4]/div/nav/ul/li[3]/div/div/section[1]/ul'  # x-path to extract men shoe category
        self.WOMEN_CATEGORY = '/html/body/div[1]/div[1]/header/div[4]/div/nav/ul/li[2]/div/div/section[1]/ul'  # x-path to extract wommen shoe category
        self.ITEM_PRICE = '/html/body/div[1]/div[1]/div[1]/main/div/div/div/div[2]/div[1]/div/div[1]/div[2]/div/div[1]/div[2]/div[1]/span'
        self.ITEM_BRAND = '/html/body/div[1]/div[1]/div[1]/main/div/div/div/div[2]/div[1]/div/div[1]/div[2]/div/div[1]/h1/div/span[1]/a/span'
        self.ITEM_NAME = '/html/body/div[1]/div[1]/div[1]/main/div/div/div/div[2]/div[1]/div/div[1]/div[2]/div/div[1]/h1/div/span[2]'

    def get_html_page(self, url: str):
        """
        Method to fetch html document from the given url.
        :return: lxml.html object.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}  # Useragent, else will get 403
            page = requests.get(url, headers=headers)
            if page.status_code == 200:
                return html.fromstring(page.content)  # To convert html string to lxml.html object
            else:
                logging.error(f"Fetching html page failed: status_code={str(page.status_code)}")
        except Exception as e:
            logging.error(f"Fetching html page failed: {str(e)}")
            raise e

    def get_category(self, xpath: str):
        """
        To get categories according to xpath.
        :param xpath: Xpath can be of women or men shoe category.
        :return: dict of categories as keys and category-url as value
        """
        try:
            html_page = self.get_html_page(self.URL)
            category_list = html_page.xpath(xpath)
            for ul in category_list:
                categories = {x[0].text: x[0].attrib['href'] for x in ul if x[0].text is not None}
                if categories:
                    return categories
        except Exception as e:
            logging.error(f"Fetching category failed: {str(e)}")
            raise e

    def get_single_item_details(self, item_url: str, xpath: str, type: str = 'name'):
        """
        To fetch single item's details from item url.
        :param item_url: URL of the item.
        :param xpath: Xpath to fetch text from item description page.
        :param type: what to extract? name/price # name and price vary in html elements in item description page.
        :return: return extracted data. Text.
        """
        html_page = self.get_html_page(item_url)
        category_list = html_page.xpath(xpath)
        if type == 'price':
            return category_list[0].attrib['content']
        elif type == 'name':
            return category_list[0].text

    def get_item_details(self, item_url):
        """
        Calls single item details for every item of interest.
        :param item_url: Url to item description.
        :return: dict of name and subname and price.
        """
        price = self.get_single_item_details(item_url, self.ITEM_PRICE, 'price')
        name = self.get_single_item_details(item_url, self.ITEM_BRAND, 'name')
        subname = self.get_single_item_details(item_url, self.ITEM_NAME, 'name')
        return {"name": name, "subname": subname, "price": price}

    def get_all_product_urls(self, url):
        """
        To fetch all product urls from product list page. In this case, category of interest.
        :param url: url to fetch data.
        :return: returns list of urls.
        """
        page = self.get_html_page(url)
        items = page.xpath('//*[@id="products"]')
        urls = [item[0].attrib['href'] for item in items[0].findall('article')]
        return urls

    def get_all_products_from_suburl(self, sub_url, category):
        """
        To get all items from a category.
        :param sub_url: category url
        :param category: category to insert into database
        :return: scraped data with category
        """
        items = self.get_all_product_urls(sub_url)
        all_items = []
        count = 0
        for item in items:
            item_details = self.get_item_details(self.URL + item)
            item_details["category"] = category
            item_details["url"] = self.URL + item
            count += 1
            print(f"SCRAPED: {count}: {item_details} ")
            all_items.append(item_details)
        return all_items

    def get_all_products(self, xpath):
        """
        To iterate through all categories and extract data from pages.
        :param xpath: xpath for the category.
        :return: list of scraped products.
        """
        categories = self.get_category(xpath)
        for category, sub_url in categories.items():
            item_details = self.get_all_products_from_suburl(self.URL + sub_url, category)
            return item_details

    def get_men_category(self):
        men = self.get_category(self.MEN_CATEGORY)
        db = SqliteDB("plugins/zappos.db")
        for item in men:
            insert_sql = "INSERT INTO category(type,categories) values(?,?)"
            insert_data = tuple(["men", item])
            db.insert_update_delete_data(insert_sql, insert_data)
        return men

    def get_women_category(self):
        women = self.get_category(self.WOMEN_CATEGORY)
        db = SqliteDB("plugins/zappos.db")
        for item in women:
            insert_sql = "INSERT INTO category(type,categories) values(?,?)"
            insert_data = tuple(["women", item])
            db.insert_update_delete_data(insert_sql, insert_data)
        return women

    def get_men_shoes(self):
        men = self.get_all_products(self.MEN_CATEGORY)
        db = SqliteDB("plugins/zappos.db")
        for item in men:
            print(item['name'], item['subname'], item['price'], item['category'], item['url'])
            insert_sql = "INSERT INTO products(type,brand,name,price,category,url) VALUES (?,?,?,?,?,?)"
            insert_data = tuple(["men", item['name'], item['subname'], item['price'], item['category'], item['url']])
            db.insert_update_delete_data(insert_sql, insert_data)
        return men

    def get_women_shoes(self):
        women = self.get_all_products(self.WOMEN_CATEGORY)
        db = SqliteDB("plugins/zappos.db")
        for item in women:
            print(item['name'], item['subname'], item['price'], item['category'], item['url'])
            insert_sql = "INSERT INTO products(type,brand,name,price,category,url) VALUES (?,?,?,?,?,?)"
            insert_data = tuple(["women", item['name'], item['subname'], item['price'], item['category'], item['url']])
            db.insert_update_delete_data(insert_sql, insert_data)
        return women

# {'name': 'Flatheads', 'subname': 'Luft', 'price': '69.95', 'category': 'Sneakers & Athletic',
# 'url': 'https://www.zappos.com/p/flatheads-luft-azure/product/9618855/color/9712'}
