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

        download_previously_data = request.form.get('select')
        filter = request.form.get('select2')
        Update = request.form.get('select3')

        checkbox = request.form.get("checkbox")
        sale = request.form.get("sale")

        if download_previously_data:

            res = database.get_goods(download_previously_data, checkbox_status, sale_status)
            date = database.get_date(download_previously_data)

            return render_template('main.html', name=res, split_colors=split_colors, split_price=split_price,
                                   req=download_previously_data, req_list=req_list, is_parsing=False, date=date,
                                   dns_sale=database.get_goods_with_max_sale(download_previously_data, checkbox_status)[1], citilink_sale=database.get_goods_with_max_sale(download_previously_data, checkbox_status)[0], organaze_sale=organaze_sale)
        elif Update:

            database.delete_request(Update)

            try:
                A.Parse(Update)
            except (BrandERR, EMPTY) as err:
                return render_template('main.html', name=name, err=err.err_decr, req=Update)
            except:
                database.delete_request(Update)
                return render_template('main.html', name=name, err="Попробуйте снова.", req=Update)

            date = database.get_date(Update)
            res = database.get_goods(Update, checkbox_status, sale_status)

            return render_template('main.html', name=res, split_colors=split_colors, split_price=split_price,
                                   req=Update,
                                   req_list=req_list, is_parsing=True, date=date,
                                   dns_sale=database.get_goods_with_max_sale(Update, checkbox_status)[1], citilink_sale=database.get_goods_with_max_sale(Update, checkbox_status)[0], organaze_sale=organaze_sale)

        elif filter:

            if checkbox == "on":
                checkbox_status = False
            if sale == "on":
                sale_status = True

            res = database.get_goods(filter, checkbox_status, sale_status)
            date = database.get_date(filter)

            return render_template('main.html', name=res, split_colors=split_colors, split_price=split_price,
                                   req=filter.lower(), req_list=req_list, is_parsing=False, date=date,
                                   dns_sale=database.get_goods_with_max_sale(filter.lower(), checkbox_status)[1], citilink_sale=database.get_goods_with_max_sale(filter.lower(), checkbox_status)[0], organaze_sale=organaze_sale)
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
