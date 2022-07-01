from ast import arguments
from lib2to3.pytree import convert
import constants
from flask_restful import Api, Resource, reqparse
from flask import Response
from mongoConnection import MongoConnection
import json
import sys
sys.path.insert(0, '../..')


def handleException(error):
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


class TransactionFilter(Resource):

    def convertDateToEpoch(self, args):
        return args[constants.startDateParameter], args[constants.endDateParameter]

    def getArgs(self):
        transactionReqParser = reqparse.RequestParser()
        transactionReqParser.add_argument(
            constants.startDateParameter, type=int, help="start date is needed for this request", required=True)
        transactionReqParser.add_argument(
            constants.endDateParameter, type=int, help="endDate date is needed for this request", required=True)
        transactionReqParser.add_argument(
            constants.userIdParameter, type=str, help="userId is needed")
        transactionReqParser.add_argument(
            constants.processIdParameter, type=str, help="processId is needed")
        args = transactionReqParser.parse_args()
        return args

    def createQuery(self, args):
        query = {}
        startDateEpoch, endDateEpoch = self.convertDateToEpoch(args)
        print(startDateEpoch, endDateEpoch)
        query[constants.tnxCollectionTimeOfTransaction] = {
            "$lte": endDateEpoch, "$gte": startDateEpoch}
        if args[constants.processIdParameter] != None:
            print(args[constants.processIdParameter])
            process = args[constants.processIdParameter]
            query["$or"] = [
                {
                    constants.tnxCollectionToProcess: {"$eq": process}
                },
                {
                    constants.tnxCollectionFromProcess: {"$eq": process}
                }
            ]
        if args[constants.userIdParameter] != None:
            user = args[constants.userIdParameter]
            query["$or"] = [
                {
                    constants.tnxCollectionFromUserId: {"$eq": user}
                },
                {
                    constants.tnxCollectionToUserId: {"$eq": user}
                }
            ]
        return query

    def get(self):
        mongo = MongoConnection.mongoClient
        db = mongo[constants.mongoInventoryDb]
        args = self.getArgs()
        try:
            query = self.createQuery(args)
            print(query)
            transactionData = list(
                db[constants.mongoTransactionCollection].find(query))
            for transaction in transactionData:
                transaction[constants.id] = str(transaction[constants.id])
            return Response(
                response=json.dumps(transactionData),
                status=200,
                mimetype="application/json"
            )
        except Exception as e:
            return handleException(e)
