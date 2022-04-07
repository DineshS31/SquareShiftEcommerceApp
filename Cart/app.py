import requests
import settings
import json
from flask import Flask, request, Response


app = Flask(__name__)


@app.route("/cart/add_item", methods=['POST'])
def add_item():
    req_payload = request.get_json()
    result = {}
    status_code = 200
    if "product_id" not in req_payload or "quantity" not in req_payload:
        result['success'] = False
        result['message'] = "Product Id & Quantity is required!"
        status_code = 400
    else:
        url = settings.cart_add_item_url
        response = requests.request("POST", url, json=req_payload)
        if response.status_code == 200:
            result = response.json()
        else:
            result['success'] = False
            result['message'] = "Error in adding item to cart!"
            status_code = 500
    return Response(json.dumps(result),
                    status=status_code,
                    mimetype="application/json")


@app.route("/cart/list_items")
def list_items():
    url = settings.cart_list_item_url
    response = requests.request("GET", url)
    if response.status_code == 200:
        result = Response(json.dumps(response.json()),
                          status=response.status_code,
                          mimetype="application/json")
    elif response.status_code == 400:
        result = Response(json.dumps({"success": True, "message": "Cart is empty!"}),
                          status=response.status_code,
                          mimetype="application/json")
    else:
        result = Response(json.dumps({"success": False, "message": "Error in listing items!"}),
                          status=response.status_code,
                          mimetype="application/json")
    return result


@app.route("/cart/get_items_total", methods=['POST'])
def get_items_total():
    url = settings.cart_get_total_value_url
    req_payload = request.get_json()
    if "postal_code" not in req_payload:
        result = Response(json.dumps({"success": False, "message": "Postal code is required!"}),
                          status=400,
                          mimetype="application/json")
    else:
        response = requests.request("GET", url, params={"shipping_postal_code": req_payload['postal_code']})
        if response.status_code == 200:
            result = Response(json.dumps(response.json()),
                              status=response.status_code,
                              mimetype="application/json")
        elif response.status_code == 400:
            result = Response(json.dumps({"success": True, "message": "Cart is empty!"}),
                              status=response.status_code,
                              mimetype="application/json")
        else:
            result = Response(json.dumps({"success": False, "message": "Error in getting items total!"}),
                              status=response.status_code,
                              mimetype="application/json")
    return result


@app.route("/cart/empty_cart", methods=['POST'])
def empty_cart():
    url = settings.empty_cart_url
    req_payload = request.get_json()
    if "action" not in req_payload:
        result = Response(json.dumps({"success": False, "message": "Action is required!"}),
                          status=400,
                          mimetype="application/json")
    else:
        response = requests.request("POST", url)
        if response.status_code == 200:
            result = Response(json.dumps(response.json()),
                              status=response.status_code,
                              mimetype="application/json")
        elif response.status_code == 400:
            result = Response(json.dumps({"success": True, "message": "Bad request!"}),
                              status=response.status_code,
                              mimetype="application/json")
        else:
            result = Response(json.dumps({"success": False, "message": "Error in removing items from cart!"}),
                              status=response.status_code,
                              mimetype="application/json")
    return result


if __name__ == "__main__":
    app.run(host="localhost", debug=True)
