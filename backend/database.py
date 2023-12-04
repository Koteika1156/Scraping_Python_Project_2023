import sqlite3


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


def get_all_requests():

    """ Получение списка запросов """

    check_db()
    with sqlite3.connect('my_database.db') as con:
        cursor = con.cursor()

        r = """select * from requests"""
        cursor.execute(r)
        answ = cursor.fetchall()

    return answ


def get_goods(request, is_all):

    """ Получение товаров из БД по запросу """

    with sqlite3.connect('my_database.db') as con:
        cursor = con.cursor()

        req_id = check_requsts_list(request)[0]

        request = request.replace(" ", "%")
        first_symbol = request[0]
        request = request.replace(first_symbol, "_", 1)

        if is_all:
            query = f"SELECT * FROM goods WHERE request_id = {req_id} ORDER BY code"
        else:
            query = f"SELECT * FROM goods WHERE request_id = {req_id} AND original_name LIKE '%{request}%' ORDER BY code"

        cursor.execute(query)
        result = cursor.fetchall()

    return result


def add_request(request):

    """ Добавить запрос в таблицу запросов """

    with sqlite3.connect('my_database.db') as con:
        cursor = con.cursor()
        check_db()

        a = get_all_requests()
        pos = len(a) + 1
        cursor.execute('INSERT INTO requests (request_id, request) VALUES (?, ?)', (f'{pos}', f'{request}'))

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
            'INSERT INTO goods (original_name, name, price, shop, code, request_id) VALUES (?, ?, ?, ?, ?, ?)',
            (f'{dict["original_name"]}', f'{dict["name"]}', f'{price_str}', f'{dict["shop"]}', f'{dict["code"]}',
             f'{dict["request"]}'))

        con.commit()


def check_db():

    """ Проверка на существование таблиц """

    with sqlite3.connect('my_database.db') as con:
        cursor = con.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
        request_id INTEGER PRIMARY KEY,
        request TEXT NOT NULL
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
        FOREIGN KEY (request_id) REFERENCES requests(request_id)
        )
        ''')
