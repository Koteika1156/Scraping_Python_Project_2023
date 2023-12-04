from flask import Flask, render_template, request
from main import Parser, split_colors
import database
from exceptions import *

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def main_page(name=[], req="", err=""):
    req_list = database.get_all_requests()
    checkbox_status = True
    if request.method == 'POST':

        form_2 = request.form.get('select')
        checkbox = request.form.get("checkbox")

        if checkbox == "on":
            checkbox_status = False

        if form_2:
            res = database.get_goods(form_2, checkbox_status)
            return render_template('main.html', name=res, split_colors=split_colors, req=form_2, req_list=req_list)
        else:

            req = request.form['request']

            if req == "":
                return render_template('main.html', name=name, req_list=req_list)
            else:
                original_request = req
                req = req.lower()
                a = database.check_requsts_list(req)
                if a:
                    res = database.get_goods(a[1], checkbox_status)
                else:
                    try:
                        A.Parse(req)
                    except (BrandERR, EMPTY) as err:
                        return render_template('main.html', name=name, err=err.err_decr, req=original_request)
                    except:
                        database.delete_request(req)
                        return render_template('main.html', name=name, err="Попробуйте снова.", req=original_request)

                    res = database.get_goods(req, checkbox_status)

            return render_template('main.html', name=res, split_colors=split_colors, req=original_request,
                                   req_list=req_list)
    else:
        return render_template('main.html', name=name, req_list=req_list)


if __name__ == '__main__':
    A = Parser()
    app.run()
