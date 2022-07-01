from ast import arguments
from lib2to3.pytree import convert
import constants
from flask_restful import Api, Resource, reqparse
from flask import Response
from mongoConnection import MongoConnection
import json
import sys
sys.path.insert(0, '../..')


class UserById(Resource):

    def handleException(self, error):
        print("============== ERROR handleException ===============")
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

    def getArgs(self):
        userReqParser = reqparse.RequestParser()
        userReqParser.add_argument(
            constants.userIdParameter, type=str, help="userId is needed", required=True)
        args = userReqParser.parse_args()
        return args

    def createQuery(self, args):
        query = {constants.userCollectionUserId: {
            "$eq": args[constants.userIdParameter]}}
        return query

    def get(self):
        mongo = MongoConnection.mongoClient
        db = mongo[constants.mongoInventoryDb]
        args = self.getArgs()
        print(args)
        try:
            query = self.createQuery(args)
            print(query)
            userData = list(
                db[constants.mongoUserCollection].find(query))
            for user in userData:
                user[constants.id] = str(user[constants.id])
            return Response(
                response=json.dumps(userData),
                status=200,
                mimetype="application/json"
            )
        except Exception as e:
            return self.handleException(e)
