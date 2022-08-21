from controllers.user.userById import UserById
from controllers.user.userAccounting import UserAccounting
from controllers.transaction.TransactionFilter import TransactionFilter
from controllers.process.processAccounting import ProcessAccounting
from controllers.staticReport.staticStock import StockReport
import os
from flask import Flask, request, Response
import json
from flask_restful import Api, Resource
import constants
from mongoConnection import MongoConnection


app = Flask(__name__)
api = Api(app)

MongoConnection.mongoConnect()
mongo = MongoConnection.mongoClient
inventoryDb = mongo.inventory


#####################   Add resources ##############################
api.add_resource(TransactionFilter, "/transactionFilter")
api.add_resource(UserById, "/userById")
api.add_resource(UserAccounting, "/userAccounting")
api.add_resource(ProcessAccounting, "/processAccounting")
api.add_resource(StockReport, "/StockReport")

##################### welcome ###############################


@app.route("/", methods=["get"])
def welcome():
    try:
        currentDir = os.path.dirname(__file__)
        filename = os.path.join(
            currentDir, constants.welcomeJsonFileRelativePath)
        print(filename)
        f = open(filename)
        welcomeMessage = json.load(f)
        welcomeMessageJson = json.dumps(welcomeMessage)
        print(welcomeMessageJson)
        return Response(
            response=welcomeMessageJson,
            status=200,
            mimetype="application/json"
        )
    except Exception as e:
        return handleResponse(e)

##################### Get User By phone number ###############################


@app.route("/userByNumber", methods=["get"])
def getUserByNumber():
    try:
        userData = list(inventoryDb.user.find())
        for user in userData:
            user["_id"] = str(user["_id"])
        print(userData)
        return Response(
            response=json.dumps(userData),
            status=200,
            mimetype="application/json"
        )
    except Exception as e:
        return handleResponse(e)


##################### Create/Post User ###############################
@app.route("/user", methods=["post"])
def create_user():
    try:
        requestJson = request.get_json()
        user = requestJson
        dbResponse = inventoryDb.user.insert_one(user)
        print("post id - "+str(dbResponse.inserted_id))
        return Response(
            response=json.dumps({
                "messge": "user created",
                "_id": f"{dbResponse.inserted_id}"}),
            status=200,
            mimetype="application/json"
        )
    except Exception as e:
        return handleResponse(e)


#####################   error handleResponse ##############################


def handleResponse(error):
    print("============== ERROR handleResponse ===============")
    print(error)
    errorStr = str(error)
    return Response(
        response=json.dumps({
            "messge": "Bad Request",
            "Error": errorStr
        }),
        status=500,
        mimetype="application/json"
    )


if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0")
