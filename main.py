import requests
import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import json
from multiprocessing import Pool

from exceptions import *
import database
from functions import *


# DNS парсит скидки а не цены(Ноутбук MSI)
# Добавить URL

class Parser:
    __cookies = {}
    __headers = {}
    __citilinkHeaders = {}
    __request = ""

    def __init__(self):
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.660 YaBrowser/23.9.5.660 Yowser/2.5 Safari/537.36',
            'X-Csrf-Token': 'uRFWgTBPbDaq7W9PW6vv2HxdHW-gVBJk2jAVTNirj92PaxS5dDk9fZiqCxgwxqWWE2l_X8INQiuPciMD6J7lsg==',
            'X-Requested-With': 'XMLHttpRequest'}
        self.__citilinkHeaders = {'authority': 'rpc.citilink.ru', 'x-grpc-web': '1', }

    def Parse(self, request):
        self.__request = database.add_request(request)

        Dns_data_list = self.Dns_parse(request)
        Dns_data_list = self.organize_data(Dns_data_list)
        self.add_to_db(Dns_data_list)

        Citilink_data_list = self.Citilink_parse(request)
        Citilink_data_list = self.organize_data(Citilink_data_list)
        self.add_to_db(Citilink_data_list)

    def Dns_parse(self, request):
        self.check_cookie()
        url_list = self.ulr_to_parse(request, "dns")
        if len(url_list) != 0:
            p = Pool(processes=10)
            return p.map(self.dns_url_parse, url_list)
        else:
            return 0

    def Citilink_parse(self, request):
        url_list = self.ulr_to_parse(request, "citilink")
        if len(url_list) != 0:
            p = Pool(processes=10)
            return p.map(self.citilink_url_parse, url_list)
        else:
            return 0

    def check_cookie(self):
        r = requests.get('https://dns-shop.ru/', cookies=self.__cookies)

        if r.status_code == 401:
            driver = uc.Chrome()
            driver.get("https://www.dns-shop.ru/")
            time.sleep(1)

            cookies = driver.get_cookies()
            driver.close()

            for i in reversed(cookies):
                if i.get("name") == 'qrator_jsid':
                    cookie_value = i.get("value")
                    break

            self.__cookies = dict(
                cookies_are=f'current_path=0ade23fd6a439b986198c2aac1213be47601fdc95f22e1ed4bdbc2f5a7d45646a%3A2%3A%7Bi%3A0%3Bs%3A12%3A%22current_path%22%3Bi%3A1%3Bs%3A109%3A%22%7B%22city%22%3A%22a9f47dbf-f564-11de-97f8-00151716f9f5%22%2C%22cityName%22%3A%22%5Cu041f%5Cu0435%5Cu0440%5Cu043c%5Cu044c%22%2C%22method%22%3A%22manual%22%7D%22%3B%7D; lang=ru; city_path=perm; qrator_jsid={cookie_value}')

    def ulr_to_parse(self, request, shop):
        request = request.strip()
        request = request.replace(" ", "+")

        if shop == "dns":
            r = requests.get(f'https://www.dns-shop.ru/search/?q={request}&p=1&stock=now-today-tomorrow-later',
                             cookies=self.__cookies)
        else:
            r = requests.get(f'https://www.citilink.ru/search/?text={request}&p=1', headers=self.__citilinkHeaders)
            if len(r.text) < 150:
                driver = uc.Chrome()
                driver.get("https://www.citilink.ru/")
                time.sleep(1)
                driver.close()
                r = requests.get(f'https://www.citilink.ru/search/?text={request}&p=1', headers=self.__citilinkHeaders)

        bs = BeautifulSoup(r.text, 'lxml')

        if bs.find_all('div', {'class': 'brands-page'}) or bs.find_all('div', {
            'class': 'ekkbt9g0 react-ssr-brandzones-2cypjf e1fcwjnh0'}):
            database.delete_request(request)
            raise BrandERR

        if shop == "dns":
            if bs.find_all('div', {'class': 'empty-search-results'}) or bs.find_all('div', {'class': 'low-relevancy'}):
                database.delete_request(request)
                raise EMPTY
            found_count_pages = bs.find_all('li', {'class': 'pagination-widget__page'})
            if found_count_pages:
                url_list = [f'https://www.dns-shop.ru/search/?q={request}&p={i}&stock=now-today-tomorrow-later' for i in
                            range(1, int(found_count_pages[-1].get("data-page-number")) + 1)]
            else:
                url_list = [f'https://www.dns-shop.ru/search/?q={request}&p=1&stock=now-today-tomorrow-later']
        else:
            if bs.find_all('div', {'class': 'ProductCardCategoryList__pagination'})[0].get_text():
                found_count_pages = bs.find_all('a', {
                    'class': 'PaginationWidget__page js--PaginationWidget__page PaginationWidget__page_last PaginationWidget__page-link'})
                if len(found_count_pages) == 0:
                    found_count_pages = bs.find_all('a', {
                        'class': 'PaginationWidget__page js--PaginationWidget__page PaginationWidget__page_next PaginationWidget__page-link'})
                url_list = [f'https://www.citilink.ru/search/?text={request}&p={i}' for i in
                            range(1, int(found_count_pages[-1].get("data-page")) + 1)]
            else:
                url_list = [f'https://www.citilink.ru/search/?text={request}&p=1']

        return url_list

    def dns_url_parse(self, url):
        goods = []

        time.sleep(random.randint(1, 5))
        r = requests.get(url, cookies=self.__cookies)

        bs = BeautifulSoup(r.text, 'lxml')
        found_goods = bs.find_all('div', {'class': 'catalog-product ui-button-widget'})

        data = 'data={"type":"product-buy","containers":['

        for good in found_goods:
            id = random_string()
            data = data + f'{{"id":"as-{id}","data":{{"id":"{good.get("data-code")}"}}}},'

        data = data[0:len(data) - 1] + "]}"

        a = requests.get('https://www.dns-shop.ru/ajax-state/product-buy/', cookies=self.__cookies, data=data,
                         headers=self.__headers)
        a = json.loads(a.text)

        for i in a["data"]["states"]:
            good_name = i['data']['name']
            dict = i['data']['price']
            good_price = min(dict.values())
            goods.append({'original_name': good_name, 'name': good_name, 'price': good_price, 'shop': "DNS",
                          'request': self.__request})

        return goods

    def citilink_url_parse(self, url):
        goods = []

        time.sleep(random.randint(1, 5))
        r = requests.get(url, headers=self.__citilinkHeaders)

        bs = BeautifulSoup(r.text, 'lxml')
        found_goods = bs.find_all('div', {'class': 'ProductCardVerticalLayout ProductCardVertical__layout'})

        for good in found_goods:
            good_name = good.find('a', {'class': 'ProductCardVertical__name Link js--Link Link_type_default'}).get(
                "title")
            if good.find(string=re.compile('Нет в наличии')) is None:
                # oldPrice = good.find('span', {'class':'ProductCardVerticalPrice__price-old_current-price js--ProductCardVerticalPrice__price-old_current-price'})
                good_price = int(good.find('span', {
                    'class': 'ProductCardVerticalPrice__price-current_current-price js--ProductCardVerticalPrice__price-current_current-price'}).text.strip().replace(
                    " ", ""))
            else:
                continue

            goods.append({'original_name': good_name, 'name': good_name, 'price': good_price, 'shop': "Citilink",
                          'request': self.__request})

        return goods

    def add_to_db(self, data_list):
        first = data_list[0]
        for i in data_list:
            if first == i:
                continue
            if i["code"] == first["code"]:
                i_list = list(i["price"])
                for k in i_list:
                    first["price"][k] = i["price"][k]
            else:
                database.insert_db(first)
                first = i
        database.insert_db(first)

    def organize_data(self, data_list):
        data_list = restruct(data_list)
        data_list = sorted(data_list, key=lambda x: (x["name"], -x["price"]))
        p = Pool(processes=25)
        data_list = p.map(remove_unnecessary, data_list)
        return data_list
