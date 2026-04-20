from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Создаем базу данных прямо в файле
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
db = SQLAlchemy(app)

# Модель товара для маркетплейса
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Integer)
    description = db.Column(db.String(200))

# Главная страница
@app.route('/')
def index():
    items = Product.query.all()
    return render_template('index.html', products=items)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Если база пустая, добавим тестовый товар
        if not Product.query.first():
            test_item = Product(name="Мед локальный", price=500, description="От пасечника Иванова")
            db.session.add(test_item)
            db.session.commit()
    app.run(debug=True)