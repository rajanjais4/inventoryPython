# from flask import Flask, render_template
# from flask_pymongo import PyMongo

# app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"

# appDb = Flask(__name__)
# appDb.config["MONGO_URI"] = "mongodb+srv://inventory-admin:inventory123@inventory.rbcanbq.mongodb.net/?retryWrites=true&w=majority"
# mongo = PyMongo(appDb)

# @app.route("/db")
# def home_page():
#     print(mongo)
#     users_collection = mongo.db.list_collection_names
#     # users_collection.insert({'name':"userName1"})
#     print(users_collection)
#     return "<h1>online_users</h1>"


# if __name__ == '__main__':
#     app.run(debug=True)