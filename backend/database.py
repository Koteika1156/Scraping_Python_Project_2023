import sqlite3
import datetime

def check_db():
    """ Проверка на существование таблиц """

    with sqlite3.connect('my_database.db') as con:
        cursor = con.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
        request_id INTEGER PRIMARY KEY,
        request TEXT NOT NULL,
        successful bool NOT NULL,
        request_time TEXT NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS goods (
        id INTEGER PRIMARY KEY,
        original_name TEXT NOT NULL,
        name TEXT NOT NULL,
        price TEXT NOT NULL,
        shop TEXT NOT NULL,
        code TEXT NOT NULL,
        request_id TEXT NOT NULL,
        url TEXT NOT NULL,
        rating TEXT NOT NULL,
        sale TEXT NOT NULL,
        max_sale INTEGER NOT NULL,
        FOREIGN KEY (request_id) REFERENCES requests(request_id)
        )
        ''')

def change_request(req):
    """ В конце парсинга устанавливает запросу флаг, что парсинг прошел успешно """

    with sqlite3.connect('my_database.db') as con:
        cursor = con.cursor()
        cursor.execute(f'UPDATE requests SET successful = {True} WHERE request = "{req}"')

        con.commit()


def delete_request(req):
    """ Удаление добавленных товаров и запроса, в случае возникновения ошибки"""

    with sqlite3.connect('my_database.db') as con:
        cursor = con.cursor()
        req_id = check_requsts_list(req)[0]
        cursor.execute('DELETE FROM goods WHERE request_id = ?', (req_id,))
        cursor.execute('DELETE FROM requests WHERE request = ?', (req,))

        con.commit()


def check_requsts_list(value_to_check):
    """ Проверка на существование в БД запроса """

    with sqlite3.connect('my_database.db') as con:
        cursor = con.cursor()
        check_db()

        cursor.execute("SELECT * FROM requests WHERE request = ?", (value_to_check,))
        result = cursor.fetchone()

    return result


def check_requests():
    """ Удаляет неуспешные запросы и связанные с ними товары из бд """

    with sqlite3.connect('my_database.db') as con:
        cursor = con.cursor()
        cursor.execute("SELECT request_id FROM requests WHERE successful = ?", (False,))
        del_list = cursor.fetchall()
        for i in del_list:
            cursor.execute(f"DELETE FROM goods WHERE request_id = '{i[0]}'")
            cursor.execute(f"DELETE FROM requests WHERE request_id = '{i[0]}'")


def get_all_requests():
    """ Получение списка запросов """

    check_db()
    check_requests()
    with sqlite3.connect('my_database.db') as con:
        cursor = con.cursor()

        r = """select * from requests"""
        cursor.execute(r)
        answ = cursor.fetchall()

    return answ

def get_goods_with_max_sale(request, is_all):
    with sqlite3.connect('my_database.db') as con:
        cursor = con.cursor()
        request.lower()
        req_id = check_requsts_list(request)[0]

        request = request.replace(" ", "%")
        first_symbol = request[0]
        request = request.replace(first_symbol, "_", 1)

        if is_all:
            Citilink_query = f'SELECT * FROM goods WHERE shop = "Citilink" AND request_id = "{req_id}" AND max_sale != 0 ORDER BY max_sale DESC LIMIT 5'
            dns_query = f'SELECT * FROM goods WHERE shop = "DNS" AND request_id = "{req_id}" AND max_sale != 0 ORDER BY max_sale DESC LIMIT 5'
        else:
            Citilink_query = f"SELECT * FROM goods WHERE shop ='Citilink' AND request_id = '{req_id}' AND max_sale != 0 AND original_name LIKE '%{request}%' ORDER BY max_sale DESC LIMIT 5"
            dns_query = f"SELECT * FROM goods WHERE shop ='DNS' AND request_id = '{req_id}' AND max_sale != 0 AND original_name LIKE '%{request}%' ORDER BY max_sale DESC LIMIT 5"

        cursor.execute(Citilink_query)
        Citilink_res = cursor.fetchall()
        cursor.execute(dns_query)
        DNS_res = cursor.fetchall()
        res = [Citilink_res, DNS_res]
        return res

def get_goods(request, is_all, is_sale):
    """ Получение товаров из БД по запросу """

    with sqlite3.connect('my_database.db') as con:
        cursor = con.cursor()

        req_id = check_requsts_list(request)[0]

        request = request.replace(" ", "%")
        first_symbol = request[0]
        request = request.replace(first_symbol, "_", 1)

        if is_all:
            if is_sale:
                query = f"SELECT * FROM goods WHERE request_id = {req_id} AND CAST(SUBSTRING(price, INSTR(price, '#') + 1) AS SIGNED) != 0 ORDER BY code"
            else:
                query = f"SELECT * FROM goods WHERE request_id = {req_id} ORDER BY code"
        else:
            if is_sale:
                query = f"SELECT * FROM goods WHERE request_id = {req_id} AND original_name LIKE '%{request}%' AND CAST(SUBSTRING(price, INSTR(price, '#') + 1) AS SIGNED) != 0 ORDER BY code"
            else:
                query = f"SELECT * FROM goods WHERE request_id = {req_id} AND original_name LIKE '%{request}%' ORDER BY code"

        cursor.execute(query)
        result = cursor.fetchall()

    return result

def get_date(req):
    with sqlite3.connect('my_database.db') as con:
        cursor = con.cursor()
        check_db()

        cursor.execute(f"SELECT request_time FROM requests WHERE request = '{req}'")

        a = cursor.fetchall()
        return a[0][0]


def add_request(request):
    """ Добавить запрос в таблицу запросов """

    with sqlite3.connect('my_database.db') as con:
        cursor = con.cursor()
        check_db()

        cursor.execute("SELECT * FROM requests ORDER BY request_id DESC LIMIT 1")

        a = cursor.fetchall()
        if a:
            pos = a[0][0] + 1
        else:
            pos = 1

        now = datetime.datetime.now().replace(microsecond=0)
        cursor.execute('INSERT INTO requests (request_id, request, successful, request_time) VALUES (?, ?, ?, ?)',
                       (f'{pos}', f'{request}', False, now))

        con.commit()

    return pos


def insert_db(dict):
    """ Добавить товар в таблицу товаров """

    with sqlite3.connect('my_database.db') as con:
        cursor = con.cursor()

        price_str = ""
        k = 0
        i_list = list(dict["price"])

        for i in dict["price"]:
            price_str = price_str + f"{i}" + ":" + f"{dict['price'][f'{i}']}"
            k += 1
            if k == len(i_list):
                break
            else:
                price_str = price_str + ","

        cursor.execute(
            'INSERT INTO goods (original_name, name, price, shop, code, request_id, url, rating, sale, max_sale) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (f'{dict["original_name"]}', f'{dict["name"]}', f'{price_str}', f'{dict["shop"]}', f'{dict["code"]}',
             f'{dict["request"]}', f'{dict["url"]}', f'{dict["rating"]}', f'{dict["sale"]}', f'{dict["max_sale"]}'))

        con.commit()

