from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

api = Api(app)
db = SQLAlchemy(app)

# Моделі
class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    items = db.relationship("Item", backref="store", lazy="dynamic")

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("store.id"), nullable=False)

# Ресурси
class StoreResource(Resource):
    def post(self):
        data = request.get_json()
        store = Store(name=data["name"])
        db.session.add(store)
        db.session.commit()
        return {"message": "Store created", "store": {"id": store.id, "name": store.name}}, 201

    def get(self):
        stores = Store.query.all()
        return {"stores": [{"id": s.id, "name": s.name, "items": [item.id for item in s.items]} for s in stores]}

class ItemResource(Resource):
    def post(self):
        data = request.get_json()
        item = Item(name=data["name"], price=data["price"], store_id=data["store_id"])
        db.session.add(item)
        db.session.commit()
        return {
            "message": "Item created",
            "item": {
                "id": item.id,
                "name": item.name,
                "price": item.price,
                "store_id": item.store_id,
            },
        }, 201

    def get(self):
        items = Item.query.all()
        return {
            "items": [
                {"id": i.id, "name": i.name, "price": i.price, "store_id": i.store_id}
                for i in items
            ]
        }, 200

# Реєстрація ресурсів
api.add_resource(StoreResource, "/store")
api.add_resource(ItemResource, "/item")

@app.route("/")
def home():
    return {"message": "API працює з SQLAlchemy та One-to-Many!"}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)