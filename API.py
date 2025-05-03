from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super-secret-key"  # Заміни на надійний секрет
api = Api(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Таблиця-зв’язка для many-to-many
store_categories = db.Table(
    'store_categories',
    db.Column('store_id', db.Integer, db.ForeignKey('store.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

# Моделі
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    items = db.relationship("Item", backref="store", lazy=True)
    categories = db.relationship("Category", secondary=store_categories, backref="stores")

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("store.id"), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

# Ендпоінти для аутентифікації
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return {"message": "User already exists"}, 400

    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return {"message": "User created"}, 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return {"access_token": access_token}, 200

    return {"message": "Invalid credentials"}, 401

# Захищені ресурси
class StoreResource(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        store = Store(name=data["name"])
        db.session.add(store)
        db.session.commit()
        return {"message": "Store created", "store": {"id": store.id, "name": store.name}}, 201

class ItemResource(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        item = Item(name=data["name"], price=data["price"], store_id=data["store_id"])
        db.session.add(item)
        db.session.commit()
        return {"message": "Item created", "item": {"id": item.id, "name": item.name, "price": item.price}}, 201

    @jwt_required()
    def get(self):
        items = Item.query.all()
        return {"items": [{"id": i.id, "name": i.name, "price": i.price, "store_id": i.store_id} for i in items]}, 200

class CategoryResource(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        category = Category(name=data["name"])
        db.session.add(category)
        db.session.commit()
        return {"message": "Category created", "category": {"id": category.id, "name": category.name}}, 201

class StoreCategoryLinkResource(Resource):
    @jwt_required()
    def post(self, store_id):
        data = request.get_json()  # {"category_ids": [1, 2]}
        store = Store.query.get_or_404(store_id)
        categories = Category.query.filter(Category.id.in_(data["category_ids"])).all()
        store.categories.extend(categories)
        db.session.commit()
        return {"message": "Categories linked to store"}, 200

    @jwt_required()
    def get(self, store_id):
        store = Store.query.get_or_404(store_id)
        return {
            "store": store.name,
            "categories": [c.name for c in store.categories]
        }

# Реєстрація ресурсів
api.add_resource(StoreResource, "/store")
api.add_resource(ItemResource, "/item")
api.add_resource(CategoryResource, "/category")
api.add_resource(StoreCategoryLinkResource, "/store/<int:store_id>/categories")

@app.route("/")
def home():
    return {"message": "API працює з JWT, SQLAlchemy, One-to-Many та Many-to-Many!"}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)