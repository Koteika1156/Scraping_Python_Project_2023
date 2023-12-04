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


def split_colors(str_=""):

    """ Предварительная обработка цен для вывода в html шаблон """

    str_ = str_.split(",")
    new_arr = []
    for i in str_:
        new_arr.append(i.split(":"))
    return new_arr


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

    if type(dict["price"]) == int:
        dict["price"] = {"None": dict["price"]}

    code = dict["name"]

    start = code.find("[")

    if start != -1:
        code = code[:start]

    start = code.find(",")

    if start != -1:
        code = code[:start]

    code = re.sub('[а-яА-Я]', '', code)

    start = code.find('"')

    if start != -1:
        if code[start + 1] == '"' or code[start + 2] == '"':
            code.replace('""', '')
            code.replace('" "', '')
        else:
            code = code[start + 1:]

    start = code.find('(')
    if start != -1:
        end = code.find(')')
        code = code[:start] + code[end + 1:]

    dict["code"] = code.strip()

    return dict
