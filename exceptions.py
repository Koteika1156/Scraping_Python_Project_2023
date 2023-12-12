class BrandERR(Exception):

  """ Ошибка отсутствия бренда """

  err_decr = "Из-за особенностей сайтов DNS и Citilink нельзя парсить передавая в запрос только бренд. Попробуйте расширить запрос, например: Холодильник"

class EMPTY(Exception):

  """ Ошибка отсутствия товаров на странице парсинга """

  err_decr = "По вашему запросу ничего не найдено."