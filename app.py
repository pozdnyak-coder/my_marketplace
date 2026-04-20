import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

# Настройка путей (ВАЖНО для Render)
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'university_project_key_2026'
# Указываем серверу точное местоположение базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'market.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель товара
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    category = db.Column(db.String(50))

# ГЛАВНАЯ СТРАНИЦА
@app.route('/')
def index():
    products = Product.query.all()
    cart_count = sum(session.get('cart', {}).values())
    return render_template('index.html', products=products, cart_count=cart_count)

# ДОБАВЛЕНИЕ В КОРЗИНУ
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    p_id = str(product_id)
    cart[p_id] = cart.get(p_id, 0) + 1
    session['cart'] = cart
    flash('Товар добавлен!')
    return redirect(url_for('index'))

# ПРОСМОТР КОРЗИНЫ
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

# ОЧИСТКА КОРЗИНЫ
@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('view_cart'))

# ЗАПУСК И АВТОСОЗДАНИЕ БАЗЫ
if __name__ == '__main__':
    with app.app_context():
        # Эта команда создает таблицы в market.db ПРИНУДИТЕЛЬНО
        db.create_all()
        
        # Заполняем товарами, если база пустая
        if not Product.query.first():
            db.session.add_all([
                Product(name="Горный мёд", price=850, description="С пасеки в Алтае, 500г", category="Еда"),
                Product(name="Вязаный свитер", price=3200, description="Ручная работа", category="Одежда"),
                Product(name="Керамика", price=1500, description="Ручной обжиг", category="Дом"),
                Product(name="Травяной чай", price=450, description="Сбор 2025 года", category="Еда")
            ])
            db.session.commit()
            print("База данных успешно создана и заполнена!")
            
    app.run(debug=True)
