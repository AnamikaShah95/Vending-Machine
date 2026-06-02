from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import datetime
import random

app = Flask(__name__)
# FIXED: Switched from :memory: to a persistent local file database to keep transactions secure
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vending_machine.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db = SQLAlchemy(app)

# ─── RELATIONAL DATA MODEL SCHEMAS ───
class Product(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=10)
    bg_glow = db.Column(db.String(100))
    image = db.Column(db.String(2000))

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    product_name = db.Column(db.String(80))
    amount_paid = db.Column(db.Float)
    payment_mode = db.Column(db.String(20))

# ─── CORE API GATEWAYS ───
@app.route('/api/products', methods=['GET'])
def get_products():
    all_items = Product.query.all()
    return jsonify({"products": [
        {"id": p.id, "name": p.name, "price": p.price, "quantity": p.quantity, "bg_glow": p.bg_glow, "image": p.image}
        for p in all_items
    ]})

@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    simulated_temp = round(random.uniform(3.6, 4.9), 1)
    return jsonify({
        "temperature": f"{simulated_temp}°C",
        "status": "ONLINE"
    })

@app.route('/api/order/cart', methods=['POST'])
def process_cart_checkout():
    data = request.json or {}
    item_codes = data.get("cartItems", [])
    mode = data.get("transactionType", "cash")
    cash_loaded = float(data.get("insertedAmount", 0))

    if not item_codes:
        return jsonify({"success": False, "message": "Cart is empty"}), 400

    total_cost = 0.0
    verified_products = []
    
    # FIXED: Tally map captures stock reductions locally inside the loop to block over-purchasing
    temp_quantities = {}

    for code in item_codes:
        code_upper = str(code).strip().upper()
        product = Product.query.get(code_upper)
        
        if not product:
            return jsonify({"success": False, "message": f"Code {code} not found"}), 400
            
        if code_upper not in temp_quantities:
            temp_quantities[code_upper] = product.quantity
            
        if temp_quantities[code_upper] <= 0:
            return jsonify({"success": False, "message": f"{product.name} out of stock"}), 409
            
        temp_quantities[code_upper] -= 1
        total_cost += product.price
        verified_products.append(product)

    if mode == "cash" and cash_loaded < total_cost:
        return jsonify({"success": False, "message": f"Need Rs. {total_cost}"}), 422

    vended_manifest = []
    for product in verified_products:
        product.quantity -= 1  
        tx = Transaction(product_name=product.name, amount_paid=product.price, payment_mode=mode.upper())
        db.session.add(tx)
        vended_manifest.append({"name": product.name, "image": product.image})
        
    db.session.commit()
    return jsonify({
        "success": True,
        "vended": vended_manifest,
        "change": max(0.0, cash_loaded - total_cost)
    })

@app.route('/api/admin/analytics', methods=['GET'])
def get_analytics():
    total_sales = db.session.query(db.func.sum(Transaction.amount_paid)).scalar() or 0.0
    tx_count = Transaction.query.count()
    popular_item = db.session.query(Transaction.product_name, db.func.count(Transaction.id).label('qty')).group_by(Transaction.product_name).order_by(db.text('qty DESC')).first()
    
    return jsonify({
        "gross_revenue": f"Rs. {int(total_sales)}",
        "total_transactions": tx_count,
        "top_selling_product": popular_item[0].capitalize() if popular_item else "None"
    })

@app.route('/api/admin/restock', methods=['POST'])
def restock_machine():
    for p in Product.query.all():
        p.quantity = 10
    db.session.commit()
    return jsonify({"success": True})

# ─── DATABASE SEEDING ENGINE WITH EMBEDDED SVGS ───
with app.app_context():
    db.create_all()
    
    if Product.query.count() == 0:
        svg_red = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect x='32' y='15' width='36' height='70' rx='6' fill='%23ef4444'/><rect x='32' y='35' width='36' height='15' fill='%23fff' opacity='0.25'/><circle cx='50' cy='42' r='8' fill='%23fff' opacity='0.3'/></svg>"
        svg_dark_red = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect x='32' y='15' width='36' height='70' rx='6' fill='%23b91c1c'/><path d='M32,40 Q50,55 68,40' fill='none' stroke='%23fff' stroke-width='4' opacity='0.3'/></svg>"
        svg_orange = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect x='32' y='15' width='36' height='70' rx='6' fill='%23f97316'/><circle cx='50' cy='50' r='10' fill='%23fff' opacity='0.4'/></svg>"
        svg_green = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect x='32' y='15' width='36' height='70' rx='6' fill='%2322c55e'/><line x1='50' y1='25' x2='50' y2='75' stroke='%23fff' stroke-width='4' opacity='0.3'/></svg>"
        svg_lime = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect x='32' y='15' width='36' height='70' rx='6' fill='%2384cc16'/><polygon points='50,25 38,50 50,50 50,75 62,50 50,50' fill='%23fff' opacity='0.4'/></svg>"
        svg_pink = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><polygon points='32,20 68,20 60,85 40,85' fill='%23f472b6'/><path d='M32,20 Q50,8 68,20' fill='%23fce7f3'/><line x1='50' y1='8' x2='62' y2='45' stroke='%23ef4444' stroke-width='4'/></svg>"
        svg_white = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><polygon points='32,20 68,20 60,85 40,85' fill='%23fef3c7'/><path d='M32,20 Q50,8 68,20' fill='%23ffffff'/></svg>"
        svg_blue = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect x='32' y='15' width='36' height='70' rx='6' fill='%232563eb'/><circle cx='50' cy='50' r='12' fill='%23ef4444' opacity='0.6'/></svg>"
        svg_yellow = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect x='32' y='15' width='36' height='70' rx='6' fill='%23eab308'/><circle cx='50' cy='50' r='12' fill='%23ea580c' opacity='0.5'/></svg>"
        svg_emerald = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect x='32' y='15' width='36' height='70' rx='6' fill='%2310b981'/><rect x='44' y='30' width='12' height='40' rx='2' fill='%23fff' opacity='0.3'/></svg>"
        svg_amber = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect x='32' y='15' width='36' height='70' rx='6' fill='%23f59e0b'/><circle cx='50' cy='45' r='10' fill='%23fff' opacity='0.3'/></svg>"
        svg_zinc = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect x='32' y='15' width='36' height='70' rx='6' fill='%23d4d4d8'/><line x1='32' y1='40' x2='68' y2='40' stroke='%2322c55e' stroke-width='4' opacity='0.4'/></svg>"
        svg_maroon = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect x='32' y='15' width='36' height='70' rx='6' fill='%237f1111'/><circle cx='50' cy='50' r='10' fill='%23f43f5e' opacity='0.4'/></svg>"

        mock_products = [
            {"id": "A1", "name": "diet coke", "price": 40, "bg_glow": "shadow-red-500/20", "image": svg_red},
            {"id": "A2", "name": "coke", "price": 40, "bg_glow": "shadow-red-700/20", "image": svg_dark_red},
            {"id": "A3", "name": "fanta", "price": 20, "bg_glow": "shadow-orange-500/20", "image": svg_orange},
            {"id": "A4", "name": "sprite", "price": 30, "bg_glow": "shadow-green-500/20", "image": svg_green},
            {"id": "B1", "name": "mountain dew", "price": 35, "bg_glow": "shadow-lime-500/20", "image": svg_lime},
            {"id": "B2", "name": "milkshake", "price": 60, "bg_glow": "shadow-pink-400/20", "image": svg_pink},
            {"id": "B3", "name": "lassi", "price": 50, "bg_glow": "shadow-amber-100/10", "image": svg_white},
            {"id": "B4", "name": "pepsi", "price": 35, "bg_glow": "shadow-blue-600/20", "image": svg_blue},
            {"id": "C1", "name": "maaza", "price": 45, "bg_glow": "shadow-yellow-500/20", "image": svg_yellow},
            {"id": "C2", "name": "7up", "price": 35, "bg_glow": "shadow-emerald-500/20", "image": svg_emerald},
            {"id": "C3", "name": "slice", "price": 45, "bg_glow": "shadow-amber-500/20", "image": svg_amber},
            {"id": "C4", "name": "limca", "price": 35, "bg_glow": "shadow-zinc-400/10", "image": svg_zinc},
            {"id": "D1", "name": "fizz", "price": 30, "bg_glow": "shadow-red-900/30", "image": svg_maroon}
        ]
        for p in mock_products:
            db.session.add(Product(id=p["id"], name=p["name"], price=p["price"], bg_glow=p["bg_glow"], image=p["image"]))
        db.session.commit()

if __name__ == '__main__':
    app.run(port=5000, debug=True, threaded=True)