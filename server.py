from flask import Flask,request, Response
import pymongo
import json
app = Flask(__name__)

##################### Mongo Connection ##############################
mongoUri="mongodb+srv://inventory-admin:inventory123@inventory.rbcanbq.mongodb.net/test?authSource=admin&replicaSet=atlas-13oxx1-shard-0&readPreference=primary&ssl=true"
try:
    mongo =pymongo.MongoClient(mongoUri,
    serverSelectionTimeoutMs = 1000)
    mongo.server_info()
    inventoryDb=mongo.inventory
    print("mongo connection successfully")
except:
    print("Couldn't connect to Mongo'");

##################### welcome ###############################
@app.route("/", methods=["get"])
def welcome():
    try:
        return "welcome to inventory server"
    except Exception as e:
        print("============== ERROR ===============")
        print(e);
        return Response(
            response=json.dumps({
                "messge":"Bad Request"}),
            status=500,
            mimetype="application/json"
        )


##################### Get User By phone number ###############################
@app.route("/userByNumber", methods=["get"])
def getUserByNumber():
    try:
        userData=list(inventoryDb.user.find())
        for user in userData:
            user["_id"]=str(user["_id"]);
        print(userData)
        return Response(
            response=json.dumps(userData),
            status=200,
            mimetype="application/json"
        )
    except Exception as e:
        print("============== ERROR ===============")
        print(e);
        return Response(
            response=json.dumps({
                "messge":"user not found"}),
            status=500,
            mimetype="application/json"
        )

##################### Create/Post User ###############################
@app.route("/user", methods=["post"])
def create_user():
    try:
        requestJson=request.get_json()
        user=requestJson
        dbResponse=inventoryDb.user.insert_one(user)
        print("post id - "+str(dbResponse.inserted_id))
        return Response(
            response=json.dumps({
                "messge":"user created",
                "_id":f"{dbResponse.inserted_id}"}),
            status=200,
            mimetype="application/json"
        )
    except Exception as e:
        print("============== ERROR ===============")
        print(e);
###################################################
if __name__ == '__main__':
    app.run(debug=True,port=8080,host="0.0.0.0")