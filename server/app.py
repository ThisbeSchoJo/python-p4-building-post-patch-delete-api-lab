#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(  bakeries,   200  )

@app.route('/bakeries/<int:id>', methods=["GET", "PATCH"])
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()

    if bakery:
        if request.method == 'GET':
            bakery_serialized = bakery.to_dict()
            return make_response ( bakery_serialized, 200  )
        elif request.method == 'PATCH':
            for key in request.form:
                setattr(bakery, key, request.form[key])
            db.session.commit()
            response_body = bakery.to_dict()
            return make_response(response_body,200)
    else:
        response_body = {
            "error": "Bakery Not Found"
        }
        return make_response(response_body, 404)

@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    # extracts form data from the request
    data = request.form

    new_baked_good = BakedGood(
        name = data.get('name'),
        price = int(data.get('price')),
        # The following two are auto generated so don't need to define...
        # created_at = data.get('created_at'),
        # updated_at = data.get('updated_at'),
        bakery_id = int(data.get('bakery_id'))
    )

    db.session.add(new_baked_good)
    db.session.commit()

    return make_response(new_baked_good.to_dict(), 201)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response( baked_goods_by_price_serialized, 200  )
   
# @app.route('/bakeries/<int:id>', methods=['PATCH'])
# def update_bakery(id):
#     # Retrieve bakery by id from the database
#     bakery = Bakery.query.get(id)

#     if not bakery:
#         return make_response(jsonify({"error": "Bakery not found"}), 404)

#     # Extract the new name from request.form
#     new_name = request.form.get('name')
#     if new_name:
#         # Update only if new name is provided
#         bakery.name = new_name
#         db.session.commit()

#     return make_response(jsonify(bakery.to_dict()), 200)

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = db.session.get(BakedGood, id)

    if baked_good:
        db.session.delete(baked_good)
        db.session.commit()
        return make_response(jsonify({"message":"Baked good successfully deleted"}), 200)
    else:
        response_body = {
            "error": "Baked good not found"
        }
        return make_response(jsonify(response_body), 404)

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response( most_expensive_serialized,   200  )

if __name__ == '__main__':
    app.run(port=5555, debug=True)