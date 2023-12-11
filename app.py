from flask import Flask, render_template, request
from main import Parser, split_colors, split_price, organaze_sale
import database
from exceptions import *

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def main_page(name=[], req="", err=""):
    req_list = database.get_all_requests()
    checkbox_status = True
    sale_status = False
    if request.method == 'POST':

        form_2 = request.form.get('select')
        form_3 = request.form.get('select2')
        form_4 = request.form.get('select3')
        checkbox = request.form.get("checkbox")
        sale = request.form.get("sale")

        if form_2:
            res = database.get_goods(form_2, checkbox_status, sale_status)
            date = database.get_date(form_2)
            return render_template('main.html', name=res, split_colors=split_colors, split_price=split_price,
                                   req=form_2, req_list=req_list, is_parsing=False, date=date,
                                   dns_sale=database.get_goods_with_max_sale(form_2, checkbox_status)[1], citilink_sale=database.get_goods_with_max_sale(form_2, checkbox_status)[0], organaze_sale=organaze_sale)
        elif form_4:
            database.delete_request(form_4)
            try:
                A.Parse(form_4)
            except (BrandERR, EMPTY) as err:
                return render_template('main.html', name=name, err=err.err_decr, req=form_4)
            except:
                database.delete_request(form_4)
                return render_template('main.html', name=name, err="Попробуйте снова.", req=form_4)
            date = database.get_date(form_4)
            res = database.get_goods(form_4, checkbox_status, sale_status)
            return render_template('main.html', name=res, split_colors=split_colors, split_price=split_price,
                                   req=form_4,
                                   req_list=req_list, is_parsing=True, date=date,
                                   dns_sale=database.get_goods_with_max_sale(form_4, checkbox_status)[1], citilink_sale=database.get_goods_with_max_sale(form_4, checkbox_status)[0], organaze_sale=organaze_sale)

        elif form_3:

            if checkbox == "on":
                checkbox_status = False
            if sale == "on":
                sale_status = True

            res = database.get_goods(form_3, checkbox_status, sale_status)
            date = database.get_date(form_3)
            return render_template('main.html', name=res, split_colors=split_colors, split_price=split_price,
                                   req=form_3.lower(), req_list=req_list, is_parsing=False, date=date,
                                   dns_sale=database.get_goods_with_max_sale(form_3.lower(), checkbox_status)[1], citilink_sale=database.get_goods_with_max_sale(form_3.lower(), checkbox_status)[0], organaze_sale=organaze_sale)
        else:

            req = request.form['request']

            if req == "":
                return render_template('main.html', name=name, req_list=req_list)
            else:
                req = req.lower()
                a = database.check_requsts_list(req)
                is_parsing = False
                date = ""
                if a:
                    res = database.get_goods(a[1], checkbox_status, sale_status)
                    date = database.get_date(req)
                else:
                    try:
                        A.Parse(req)
                    except (BrandERR, EMPTY) as err:
                        return render_template('main.html', name=name, err=err.err_decr, req=req)
                    except:
                        database.delete_request(req)
                        return render_template('main.html', name=name, err="Попробуйте снова.", req=req)

                    res = database.get_goods(req, checkbox_status, sale_status)
                    is_parsing = True

            return render_template('main.html', name=res, split_colors=split_colors, split_price=split_price, req=req,
                                   req_list=req_list, is_parsing=is_parsing, date=date,
                                   dns_sale=database.get_goods_with_max_sale(req, checkbox_status)[1], citilink_sale=database.get_goods_with_max_sale(req, checkbox_status)[0], organaze_sale=organaze_sale)
    else:
        return render_template('main.html', name=name, req_list=req_list)


if __name__ == '__main__':
    A = Parser()
    app.run()
