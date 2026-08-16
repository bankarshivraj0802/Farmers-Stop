import os, json
from flask import Flask, request, jsonify, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "your_secret_key"

orders = []
if os.path.exists("orders.json"):
    with open("orders.json", "r") as f:
        try:
            orders = json.load(f)
        except json.JSONDecodeError:
            orders = []

vegetable_stock = {
    "Tomato": {"status": "In-Stock", "price": 40},
    "Onion": {"status": "In-Stock", "price": 30},
    "Potato": {"status": "In-Stock", "price": 25},
    "Spinach": {"status": "In-Stock", "price": 15},
    "Carrot": {"status": "In-Stock", "price": 35},
    "Cabbage": {"status": "Out-Of-Stock", "price": 20},
    "Peas": {"status": "In-Stock", "price": 50},
    "Cauliflower": {"status": "In-Stock", "price": 30}
}

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        role = request.form['role']
        if role == 'farmer':
            session['role'] = 'farmer'
            return redirect(url_for('farmer_page'))
        else:
            session['role'] = 'customer'
            return redirect(url_for('order_page'))
    return render_template("login.html")

@app.route('/farmer')
def farmer_page():
    if session.get('role') == 'farmer':
        return render_template("farmer.html", vegetables=vegetable_stock)
    return "Access Denied. Farmers only."

@app.route('/update-stock', methods=['POST'])
def update_stock():
    if session.get('role') == 'farmer':
        data = request.get_json()
        veg = data.get("vegetable")
        status = data.get("status")
        if veg in vegetable_stock:
            vegetable_stock[veg]["status"] = status
            return jsonify({"message": f"{veg} updated to {status}"})
        return jsonify({"error": "Invalid vegetable"}), 400
    return jsonify({"error": "Unauthorized"}), 403

@app.route('/update-price', methods=['POST'])
def update_price():
    if session.get('role') == 'farmer':
        data = request.get_json()
        veg = data.get("vegetable")
        price = data.get("price")
        if veg in vegetable_stock:
            vegetable_stock[veg]["price"] = float(price)
            return jsonify({"message": f"{veg} price updated to {price}"})
        return jsonify({"error": "Invalid vegetable"}), 400
    return jsonify({"error": "Unauthorized"}), 403

@app.route('/admin')
def admin_page():
    if session.get('role') == 'farmer':
        return render_template("admin.html", orders=orders)
    return "Access Denied. Farmers only."

@app.route('/order')
def order_page():
    if session.get('role') == 'customer':
        return render_template("order.html", vegetables=vegetable_stock)
    return "Access Denied. Customers only."

@app.route('/submit-order', methods=['POST'])
def submit_order():
    data = request.get_json()
    data["status"] = "Pending"

    total_amount = 0
    for veg, qty in data["vegetables"].items():
        try:
            qty = float(qty)
        except:
            qty = 0
        if qty > 0 and veg in vegetable_stock:
            price = vegetable_stock[veg]["price"]
            total_amount += qty * price

    data["total_amount"] = total_amount
    orders.append(data)

    with open("orders.json", "w") as f:
        json.dump(orders, f, indent=4)

    return jsonify({"message": "Order received successfully!", "order": data})

@app.route('/orders', methods=['GET'])
def get_orders():
    return jsonify(orders)

@app.route('/update-status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    status = request.json.get("status")
    if 0 <= order_id < len(orders):
        orders[order_id]["status"] = status
        with open("orders.json","w") as f:
            json.dump(orders,f,indent=4)
        return jsonify({"message":"Status updated"})
    return jsonify({"error":"Invalid order ID"}), 404

@app.route('/delete-order/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    if 0 <= order_id < len(orders):
        deleted = orders.pop(order_id)
        with open("orders.json","w") as f:
            json.dump(orders,f,indent=4)
        return jsonify({"message":"Order cancelled","order":deleted})
    return jsonify({"error":"Invalid order ID"}), 404

if __name__ == '__main__':
    app.run(debug=True)
