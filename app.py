from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SECRET_KEY'] = 'university_project_key_2026' # Нужно для работы корзины (сессий)
db = SQLAlchemy(app)

# Модель товара
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    category = db.Column(db.String(50))

@app.route('/')
def index():
    products = Product.query.all()
    # Считаем количество товаров в корзине для иконки
    cart_count = sum(session.get('cart', {}).values())
    return render_template('index.html', products=products, cart_count=cart_count)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    # Превращаем ID в строку, так как ключи сессии в JSON — всегда строки
    p_id = str(product_id)
    cart[p_id] = cart.get(p_id, 0) + 1
    
    session['cart'] = cart # Явно говорим Flask, что сессия изменилась
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
    with app.app_context():
        db.create_all()  # Это создаст таблицы, если их нет
        # Проверяем, есть ли товары, если нет — добавляем
        if not Product.query.first():
            p1 = Product(name="Горный мёд", price=850, description="Натуральный")
            db.session.add(p1)
            db.session.commit()
    app.run(debug=True)
