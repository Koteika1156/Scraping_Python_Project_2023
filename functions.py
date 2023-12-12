import random
import string
import re

def random_string():

    """ Функция генерации строки для получения цен товаров в ДНС """

    return ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=6
        )
    )


def sort(x=str):

    """ Сортировка для лямбда функции в main  """

    return int(x[:x.find("#")])

def split_price(str_=""):

    """ Предварительная обработка цен для вывода в html шаблон """

    str_ = str_.split("#")
    return str_

def split_colors(str_=""):

    """ Предварительная обработка цветов + цен для вывода в html шаблон """

    str_ = str_.split(",")
    new_arr = []
    for i in str_:
        new_arr.append(i.split(":"))
    return new_arr

def organaze_sale(x):

    """ Предварительная обработка скидок для вывода в html шаблон """

    split_pr = split_price(x[9])

    k = 0

    for i in split_pr:
        k += 1
        if int(i) == x[10]:
            break

    list_pr = split_colors(x[3])
    res = [list_pr[k - 1]]
    return res

def restruct(arr):

    new_arr = []
    for i in arr:
        for j in i:
            new_arr.append(j)
    return new_arr


def remove_unnecessary(dict):

    """ Обработка товара """

    name = dict["name"]

    colors_arr = ["темно фиолетовый", "темно серый", "полуночный черный", "изумрудный", "белый", "коричневый",
                  "серебристый", "пурпурный", "графитовый",
                  "серый", "синий", "черный", "красный", "желтый", "голубое озеро", "небесно голубой", "камуфляж",
                  "темно-зеленый", "зеленая мята",
                  "голубой", "фиолетовый", "зеленый", "розовый", "золотистый", "бирюзовый", "оранжевый", "графит",
                  "лаванда", "голубая фиалка",
                  "бежевый", "бордовый", "антрацит", "слоновая кость", "титан", "графитовый", "альпийский",
                  "сияющая звезда", "золотой"]

    for color in colors_arr:
        if color in name:
            dict["price"] = {color.capitalize(): dict["price"]}
            if name[name.find(color) - 2] == ",":
                dict["name"] = name.replace(color, " ")
            else:
                dict["name"] = name.replace(color, " ")
            break

    name = dict["name"]
    name = name.strip()

    if name[-1] == ",":
        name = name[:len(name) - 1]
    dict["name"] = name

    if type(dict["price"]) == str:
        dict["price"] = {"None": dict["price"]}

    code = dict["name"]
    code = re.sub('[а-яА-Я]', '', code)

    start = code.find("[")
    end = code.find("]")
    save = code[start:end + 1]

    start = code.find(",")
    if start != -1:
        code = code[:start]

    start = code.find('"')
    next = code[start + 1:].find('"')
    if start != -1:
        if next == -1:
            code.replace('"', '')
        else:
            code = code[:start] + code[next:]

    start = code.find('(')
    if start != -1:
        end = code.find(')')
        code = code[:start] + code[end + 1:]

    dict["code"] = code.strip() + " " + save

    return dict
