import requests
import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import json
from multiprocessing import Pool
from exceptions import *
import database
from functions import *
import threading
import queue


class Parser:

    __cookies = {}
    __headers = {}
    __citilinkHeaders = {}
    __request = ""
    max_sale = []

    def __init__(self):

        """ Загружаем Headers для Citilink  и DNS """

        self.__headers = {

            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.660 YaBrowser/23.9.5.660 Yowser/2.5 Safari/537.36',
            'X-Csrf-Token': 'uRFWgTBPbDaq7W9PW6vv2HxdHW-gVBJk2jAVTNirj92PaxS5dDk9fZiqCxgwxqWWE2l_X8INQiuPciMD6J7lsg==',
            'X-Requested-With': 'XMLHttpRequest'}

        self.__citilinkHeaders = {'authority': 'rpc.citilink.ru', 'x-grpc-web': '1', }

    def Parse(self, request):

        """ Основная функция парсинга """

        self.__request = database.add_request(request)

        self.check_site()

        result_queue = queue.Queue()

        t1 = threading.Thread(target=self.Dns_parse, args=(request, result_queue))
        t2 = threading.Thread(target=self.Citilink_parse, args=(request, result_queue))
        t1.start()
        t2.start()

        t1.join()
        t2.join()
        res = result_queue.get()
        res2 = result_queue.get()

        if res[0][0]["shop"] == "Citilink":
            Citilink_data_list = res
            Dns_data_list = res2
        else:
            Citilink_data_list = res2
            Dns_data_list = res

        Dns_data_list = self.organize_data(Dns_data_list)
        self.add_to_db(Dns_data_list)
        Citilink_data_list = self.organize_data(Citilink_data_list)
        self.add_to_db(Citilink_data_list)
        database.change_request(request)

    def Dns_parse(self, request, result_queue):

        """ Функция парсинга DNS """

        url_list = self.ulr_to_parse(request, "dns")
        if len(url_list) != 0:
            p = Pool(processes=15)
            res = p.map(self.dns_url_parse, url_list)
            result_queue.put(res)
            return
        else:
            return 0

    def Citilink_parse(self, request, result_queue):

        """ Функция парсинга Citilink """

        url_list = self.ulr_to_parse(request, "citilink")
        if len(url_list) != 0:
            p = Pool(processes=15)
            res2 = p.map(self.citilink_url_parse, url_list)
            result_queue.put(res2)
            return
        else:
            return 0


    def check_site(self):

        """ Предварительная проверка сайтов """

        self.check_cookie()
        self.check_citilink()

    def check_citilink(self):

        """ Проверка Citilink """

        r = requests.get(f'https://www.citilink.ru/, headers=self.__citilinkHeaders)')
        if len(r.text) < 150:
            driver = uc.Chrome()
            driver.get("https://www.citilink.ru/")
            time.sleep(1)
            driver.close()

    def check_cookie(self):

        """ Проверка DNS """

        r = requests.get('https://dns-shop.ru/', cookies=self.__cookies)

        if r.status_code == 401:

            options = uc.ChromeOptions()

            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.page_load_strategy = 'none'
            try:
                driver = uc.Chrome(options=options)
            except:
                raise
            driver.get('https://www.dns-shop.ru/')

            time.sleep(2)

            driver.execute_script("window.stop();")

            cookies = driver.get_cookies()
            driver.close()

            for i in reversed(cookies):
                if i.get("name") == 'qrator_jsid':
                    cookie_value = i.get("value")
                    break

            self.__cookies = dict(
                cookies_are=f'current_path=0ade23fd6a439b986198c2aac1213be47601fdc95f22e1ed4bdbc2f5a7d45646a%3A2%3A%7Bi%3A0%3Bs%3A12%3A%22current_path%22%3Bi%3A1%3Bs%3A109%3A%22%7B%22city%22%3A%22a9f47dbf-f564-11de-97f8-00151716f9f5%22%2C%22cityName%22%3A%22%5Cu041f%5Cu0435%5Cu0440%5Cu043c%5Cu044c%22%2C%22method%22%3A%22manual%22%7D%22%3B%7D; lang=ru; city_path=perm; qrator_jsid={cookie_value}')

    def ulr_to_parse(self, request, shop):

        """ Функция возвращает массив с ссылками для парсинга """

        request = request.strip()
        request = request.replace(" ", "+")

        if shop == "dns":
            r = requests.get(f'https://www.dns-shop.ru/search/?q={request}&p=1&stock=now-today-tomorrow-later',
                             cookies=self.__cookies)
        else:
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

        """ Парсинг 1 страницы DNS """

        goods = []

        time.sleep(random.randint(1, 5))
        r = requests.get(url, cookies=self.__cookies)

        bs = BeautifulSoup(r.text, 'lxml')
        found_goods = bs.find_all('div', {'class': 'catalog-product ui-button-widget'})

        urls = bs.find_all('a', {'class': 'catalog-product__name ui-link ui-link_black'})
        url_list = []
        for i in urls:
            url_list.append(i.get("href"))

        rating = bs.find_all('a', {'class': 'catalog-product__rating'})
        rating_list = []
        for i in rating:
            rating_list.append(i.get("data-rating"))

        data = 'data={"type":"product-buy","containers":['

        for good in found_goods:
            id = random_string()
            data = data + f'{{"id":"as-{id}","data":{{"id":"{good.get("data-code")}"}}}},'

        data = data[0:len(data) - 1] + "]}"

        a = requests.get('https://www.dns-shop.ru/ajax-state/product-buy/', cookies=self.__cookies, data=data,
                         headers=self.__headers)
        a = json.loads(a.text)
        k = 0
        j = 0
        for i in a["data"]["states"]:
            url = "https://www.dns-shop.ru" + url_list[k]
            rating = str(rating_list[j])
            k += 1
            j += 1
            good_name = i['data']['name']
            dict = i['data']['price']
            if "min" in dict:
                curr_price = dict["current"]
                old_price = dict["min"]
                sale = ((int(curr_price) - int(old_price)) / int(curr_price))
                sale = int(float('{0:0.2f}'.format(sale)) * 100)
            else:
                curr_price = dict["current"]
                old_price = "0"
                sale = "0"
            pr = str(curr_price) + "#" + str(old_price)
            goods.append(
                {'original_name': good_name, 'name': good_name, 'price': pr, 'shop': "DNS", 'request': self.__request,
                 'url': url, 'rating': rating, 'sale': sale})

        return goods

    def citilink_url_parse(self, url):

        """ Парсинг 1 страницы Citilink """

        goods = []

        time.sleep(random.randint(1, 5))
        r = requests.get(url, headers=self.__citilinkHeaders)

        bs = BeautifulSoup(r.text, 'lxml')
        found_goods = bs.find_all('div', {'class': 'ProductCardVerticalLayout ProductCardVertical__layout'})

        for good in found_goods:
            good_name = good.find('a', {'class': 'ProductCardVertical__name Link js--Link Link_type_default'}).get(
                "title")
            url = "https://www.citilink.ru" + good.find('a', {
                'class': 'ProductCardVertical__image-link Link js--Link Link_type_default'}).get("href")

            if good.find('span',
                         {'class': 'ProductCardVerticalMeta__count IconWithCount__count js--IconWithCount__count'}):
                rating = good.find('span', {
                    'class': 'ProductCardVerticalMeta__count IconWithCount__count js--IconWithCount__count'}).text.strip()
            else:
                rating = "0"

            if good.find(string=re.compile('Нет в наличии')) is None:
                if good.find('span', {
                    'class': 'ProductCardVerticalPrice__price-old_current-price js--ProductCardVerticalPrice__price-old_current-price'}):
                    oldPrice = good.find('span', {
                        'class': 'ProductCardVerticalPrice__price-old_current-price js--ProductCardVerticalPrice__price-old_current-price'}).text.strip().replace(
                        " ", "")
                    good_price = good.find('span', {
                        'class': 'ProductCardVerticalPrice__price-current_current-price js--ProductCardVerticalPrice__price-current_current-price'}).text.strip().replace(
                        " ", "")
                    sale = ((int(oldPrice) - int(good_price)) / int(oldPrice))
                    sale = int(float('{0:0.2f}'.format(sale)) * 100)
                else:
                    oldPrice = good.find('span', {
                        'class': 'ProductCardVerticalPrice__price-current_current-price js--ProductCardVerticalPrice__price-current_current-price'}).text.strip().replace(
                        " ", "")
                    good_price = "0"
                    sale = "0"
            else:
                continue
            pr = str(oldPrice) + "#" + str(good_price)
            goods.append({'original_name': good_name, 'name': good_name, 'price': pr, 'shop': "Citilink",
                          'request': self.__request, 'url': url, 'rating': rating, 'sale': sale})

        return goods

    def add_to_db(self, data_list):

        """ Обработка и добавление товара в БД """

        first = data_list[0]
        max_sale = int(first["sale"])
        max_sale_url = first["url"]
        for i in data_list:
            if first == i:
                continue
            if i["code"] == first["code"]:
                if int(i["sale"]) > max_sale:
                    max_sale = int(i["sale"])
                    max_sale_url = i["url"]
                first["sale"] = str(first["sale"]) + "#" + str(i["sale"])
                i_list = list(i["price"])
                for k in i_list:
                    first["price"][k] = i["price"][k]
            else:
                first["url"] = max_sale_url
                first["max_sale"] = max_sale
                database.insert_db(first)
                first = i
                max_sale = int(first["sale"])
                max_sale_url = first["url"]

        first["max_sale"] = max_sale
        first["url"] = max_sale_url
        database.insert_db(first)

    def organize_data(self, data_list):

        """ Предварительная обработка товара перед добавлением в бд """

        data_list = restruct(data_list)
        data_list = sorted(data_list, key=lambda x: (x["name"], -sort(x["price"])))
        p = Pool(processes=50)
        data_list = p.map(remove_unnecessary, data_list)
        return data_list
