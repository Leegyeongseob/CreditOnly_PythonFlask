from flask import Flask, render_template
from flask_cors import CORS
from routes.payPortOne.server import payment_complete
from routes.payPortOne.server import payment_tema
from routes.clothesCrolling.totolClothes import get_hm_sale_items;


app = Flask(__name__)   
CORS(app, origins=['http://localhost:8111'])
CORS(app, resources={r"/payment/*": {"origins": "http://localhost:3000"}})
CORS(app, resources={r"/date-clothes/*": {"origins": "http://localhost:3000"}})


app.add_url_rule('/payment/complete', 'payment_complete', payment_complete, methods=['POST'])
app.add_url_rule('/paymenttema/tema', 'paymenttema_tema', payment_tema, methods=['POST'])
app.add_url_rule('/date-clothes/totalClothes','get_hm_sale_items',get_hm_sale_items,methods=['GET'])






if __name__ == '__main__':
    app.run(debug=True)