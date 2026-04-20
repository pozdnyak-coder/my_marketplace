import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

# Настройка путей для сервера
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'university_project_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'market.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- МОДЕЛЬ ДАННЫХ ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    category = db.Column(db.String(50))

# --- ИНИЦИАЛИЗАЦИЯ БАЗЫ (Вне main, чтобы Gunicorn её видел) ---
with app.app_context():
    db.create_all()
    if not Product.query.first():
        db.session.add_all([
            Product(name="Горный мёд", price=850, description="С пасеки в Алтае, 500г", category="Еда"),
            Product(name="Вязаный свитер", price=3200, description="Ручная работа, шерсть", category="Одежда"),
            Product(name="Керамика", price=1500, description="Ручной обжиг, декор", category="Дом"),
            Product(name="Травяной чай", price=450, description="Сбор 2025 года, Алтай", category="Еда")
        ])
        db.session.commit()

# --- МАРШРУТЫ (ЛОГИКА) ---

@app.route('/')
def index():
    products = Product.query.all()
    cart = session.get('cart', {})
    cart_count = sum(cart.values())
    return render_template('index.html', products=products, cart_count=cart_count)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    p_id = str(product_id)
    cart[p_id] = cart.get(p_id, 0) + 1
    session['cart'] = cart
    flash('Товар добавлен в корзину!')
    return redirect(url_for('index'))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    items = []
    total_price = 0
    for p_id, quantity in cart.items():
        product = Product.query.get(int(p_id))
        if product:
            subtotal = product.price * quantity
            total_price += subtotal
            items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
    return render_template('cart.html', items=items, total_price=total_price)

@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('view_cart'))

if __name__ == '__main__':
    app.run(debug=True)
