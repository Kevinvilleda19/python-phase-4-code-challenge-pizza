#!/usr/bin/env python3
from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Restaurant, Pizza, RestaurantPizza
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

# Route to check the status of the API
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# GET /restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict(only=("id", "name", "address")) for restaurant in restaurants]), 200

# GET /restaurants/<int:id>
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        return jsonify(restaurant.to_dict(only=("id", "name", "address", "restaurant_pizzas.pizza", "restaurant_pizzas.price"))), 200
    else:
        return jsonify({"error": "Restaurant not found"}), 404

# DELETE /restaurants/<int:id>
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return make_response("", 204)
    else:
        return jsonify({"error": "Restaurant not found"}), 404

# GET /pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict(only=("id", "name", "ingredients")) for pizza in pizzas]), 200

# POST /restaurant_pizzas
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    try:
        # Validate restaurant and pizza IDs
        restaurant = Restaurant.query.get(data["restaurant_id"])
        pizza = Pizza.query.get(data["pizza_id"])

        if not restaurant or not pizza:
            return jsonify({"errors": ["Invalid restaurant or pizza ID"]}), 400

        # Create RestaurantPizza object
        restaurant_pizza = RestaurantPizza(price=data["price"], restaurant_id=data["restaurant_id"], pizza_id=data["pizza_id"])

        # Add to session and commit
        db.session.add(restaurant_pizza)
        db.session.commit()

        # Return the created object with associated restaurant and pizza details, and explicitly include `pizza_id` and `restaurant_id`
        response_data = restaurant_pizza.to_dict(only=("id", "price", "pizza", "restaurant"))
        response_data["pizza_id"] = restaurant_pizza.pizza_id
        response_data["restaurant_id"] = restaurant_pizza.restaurant_id

        return jsonify(response_data), 201

    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)
