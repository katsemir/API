from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

items = {}

class Item(Resource):
    def get(self, name):
        if name in items:
            return {"name": name, "price": items[name]}, 200
        return {"message": "Item not found"}, 404

    def post(self, name):
        if name in items:
            return {"message": "Item already exists"}, 400
        data = request.get_json()
        items[name] = data["price"]
        return {"name": name, "price": items[name]}, 201

    def delete(self, name):
        if name in items:
            del items[name]
            return {"message": "Item deleted"}, 200
        return {"message": "Item not found"}, 404

api.add_resource(Item, "/item/<string:name>")

if __name__ == "__main__":
    app.run(debug=True)