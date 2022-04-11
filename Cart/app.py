import json
import os
from flask import Flask, request, Response

app = Flask(__name__)

product_dir = os.path.join(os.path.dirname(__file__), "products.json")
cart_dir = os.path.join(os.path.dirname(__file__), "cart_items.json")
warehouse_distance_dir = os.path.join(os.path.dirname(__file__), "warehouse_distance.json")
products = json.loads(open(product_dir).read())


@app.route("/list_products")
def list_products():
    return Response(json.dumps({"status": "success", "products": products}),
                    status=200,
                    mimetype="application/json")


@app.route("/cart/add_item", methods=['POST'])
def add_item():
    req_payload = request.get_json()
    result = {}
    if "product_id" not in req_payload or "quantity" not in req_payload:
        result['status'] = False
        result['message'] = "Product Id & Quantity is required!"
        status_code = 400
    else:
        product_id = req_payload['product_id']
        quantity = req_payload['quantity']
        no_of_items_to_be_added = []
        for product_info in products:
            if product_info['id'] == int(product_id):
                no_of_items_to_be_added.append({
                    "product_id": int(product_id),
                    "description": product_info['name'],
                    "quantity": quantity
                })
        if no_of_items_to_be_added:
            with open(cart_dir, "a+") as outfile:
                outfile.seek(0)
                f = outfile.read()
                if f:
                    data = json.loads(f)
                    no_of_items_to_be_added.extend(data)
                outfile.truncate(0)
                outfile.write(json.dumps(no_of_items_to_be_added, indent=4))
            status_code = 201
            result['status'] = True
            result['message'] = "Item has been added to cart"
        else:
            status_code = 200
            result['status'] = True
            result['message'] = "Product not found! try listing products once..."

    return Response(json.dumps(result),
                    status=status_code,
                    mimetype="application/json")


@app.route("/cart/list_items")
def list_items():
    cart_items = open(cart_dir).read()
    if cart_items:
        cart_items = json.loads(cart_items)
        response = {
            "status": "success",
            "message": "Item available in the cart",
            "items": cart_items
        }
        result = Response(json.dumps(response),
                          status=200,
                          mimetype="application/json")
    else:
        result = Response(json.dumps({"message": "Cart is empty!"}),
                          status=400,
                          mimetype="application/json")

    return result


@app.route("/cart/get_items_total", methods=['POST'])
def get_items_total():
    req_payload = request.get_json()
    if "postal_code" not in req_payload:
        result = Response(json.dumps({"success": False, "message": "Postal code is required!"}),
                          status=400,
                          mimetype="application/json")
    else:
        postal_code = req_payload['postal_code']
        if postal_code not in range(465535, 465546):
            result = Response(json.dumps({"success": False,
                                          "message": "Invalid postal code, valid ones are 465535 to 465545."}),
                              status=400,
                              mimetype="application/json")
        else:
            warehouse_distance = json.loads(open(warehouse_distance_dir).read())
            distance_in_km = 0.0
            for distance_info in warehouse_distance:
                if distance_info['postal_code'] == postal_code:
                    distance_in_km = distance_info['distance_in_kilometers']
                    break
            price_value = 0
            cart_items = open(cart_dir).read()
            if cart_items:
                cart_items = json.loads(cart_items)
                for item_info in cart_items:
                    product_id = item_info['product_id']
                    product = {}
                    for product_info in products:
                        if product_info['id'] == product_id:
                            product = product_info
                            break
                    if product:
                        price_value += product.get("price", 0) * item_info['quantity']
                        discount = (price_value * float(product.get('discount_percentage', 0)))/100
                        price_value -= discount
                        item_weight_including_quantity = float(product.get("weight_in_grams", 0)) * item_info['quantity']
                        distance_price_value = calculate_distance(item_weight_including_quantity, distance_in_km,
                                                                  price_value)
                        price_value += distance_price_value

                response = {
                    "status": "success",
                    "message": f"Total value of your shopping cart is - ${price_value}"
                }
            else:
                response = {
                    "status": "success",
                    "message": "No Items has been to your cart!"
                }
            result = Response(json.dumps(response),
                              status=200,
                              mimetype="application/json")

    return result


def calculate_distance(weight_in_gms, distance_in_km, price_value):
    grams = float(weight_in_gms)
    kilograms = grams / 1000
    distance_price_value = 0.0
    if kilograms < 2 and distance_in_km < 5:
        distance_price_value = 12
    elif kilograms < 2 and (5 < distance_in_km < 20):
        distance_price_value = 15
    elif kilograms < 2 and (20 < distance_in_km < 50):
        distance_price_value = 20
    elif kilograms < 2 and (50 < distance_in_km < 500):
        distance_price_value = 50
    elif kilograms < 2 and (500 < distance_in_km < 800):
        distance_price_value = 100
    elif kilograms < 2 and distance_in_km > 800:
        distance_price_value = 220

    elif (2.01 < kilograms < 5) and distance_in_km < 5:
        distance_price_value = 14
    elif (2.01 < kilograms < 5) and (5 < distance_in_km < 20):
        distance_price_value = 18
    elif (2.01 < kilograms < 5) and (20 < distance_in_km < 50):
        distance_price_value = 24
    elif (2.01 < kilograms < 5) and (50 < distance_in_km < 500):
        distance_price_value = 55
    elif (2.01 < kilograms < 5) and (500 < distance_in_km < 800):
        distance_price_value = 110
    elif (2.01 < kilograms < 5) and distance_in_km > 800:
        distance_price_value = 250

    elif (5.01 < kilograms < 20) and distance_in_km < 5:
        distance_price_value = 16
    elif (5.01 < kilograms < 20) and (5 < distance_in_km < 20):
        distance_price_value = 25
    elif (5.01 < kilograms < 20) and (20 < distance_in_km < 50):
        distance_price_value = 30
    elif (5.01 < kilograms < 20) and (50 < distance_in_km < 500):
        distance_price_value = 80
    elif (5.01 < kilograms < 20) and (500 < distance_in_km < 800):
        distance_price_value = 130
    elif (5.01 < kilograms < 20) and distance_in_km > 800:
        distance_price_value = 270

    elif kilograms > 20.01 and distance_in_km < 5:
        distance_price_value = 21
    elif kilograms > 20.01 and (5 < distance_in_km < 20):
        distance_price_value = 35
    elif kilograms > 20.01 and (20 < distance_in_km < 50):
        distance_price_value = 50
    elif kilograms > 20.01 and (50 < distance_in_km < 500):
        distance_price_value = 90
    elif kilograms > 20.01 and (500 < distance_in_km < 800):
        distance_price_value = 150
    elif kilograms > 20.01 and distance_in_km > 800:
        distance_price_value = 300

    item_price_with_distance = distance_price_value + price_value
    return item_price_with_distance


@app.route("/cart/empty_cart", methods=['POST'])
def empty_cart():
    req_payload = request.get_json()
    if "action" not in req_payload:
        result = Response(json.dumps({"success": False, "message": "Action is required!"}),
                          status=400,
                          mimetype="application/json")
    else:
        with open(cart_dir, "w") as outfile:
            pass

        result = Response(json.dumps({"status": "success",
                                      "message": "All items have been removed from the cart !"}),
                          status=200,
                          mimetype="application/json")
    return result


if __name__ == "__main__":
    app.run(host="localhost", debug=True)
