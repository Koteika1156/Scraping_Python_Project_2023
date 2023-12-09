from flask import Flask, render_template, request
from main import Parser, split_colors, split_price
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
        checkbox = request.form.get("checkbox")
        sale = request.form.get("sale")

        if form_2:
            res = database.get_goods(form_2, checkbox_status, sale_status)
            return render_template('main.html', name=res, split_colors=split_colors, split_price=split_price,
                                   req=form_2, req_list=req_list)

        elif form_3:

            if checkbox == "on":
                checkbox_status = False
            if sale == "on":
                sale_status = True

            res = database.get_goods(form_3, checkbox_status, sale_status)
            return render_template('main.html', name=res, split_colors=split_colors, split_price=split_price,
                                   req=form_3.lower(), req_list=req_list)
        else:

            req = request.form['request']

            if req == "":
                return render_template('main.html', name=name, req_list=req_list)
            else:
                req = req.lower()
                a = database.check_requsts_list(req)
                if a:
                    res = database.get_goods(a[1], checkbox_status, sale_status)
                else:
                    try:
                        A.Parse(req)
                    except (BrandERR, EMPTY) as err:
                        return render_template('main.html', name=name, err=err.err_decr, req=req)
                    except:
                        database.delete_request(req)
                        return render_template('main.html', name=name, err="Попробуйте снова.", req=req)

                    res = database.get_goods(req, checkbox_status, sale_status)

            return render_template('main.html', name=res, split_colors=split_colors, split_price=split_price, req=req,
                                   req_list=req_list)
    else:
        return render_template('main.html', name=name, req_list=req_list)


if __name__ == '__main__':
    A = Parser()
    app.run()