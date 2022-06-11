from importlib.resources import Resource

from flask_restful import Api,Resource, reqparse
from flask import  Response
import json

transactionReqParser=reqparse.RequestParser()
transactionReqParser.add_argument("startDate",type=str,help="start date is needed for this request",required=True)
transactionReqParser.add_argument("endDate",type=str,help="endDate date is needed for this request",required=True)
transactionReqParser.add_argument("userId",type=str,help="userId is needed")
transactionReqParser.add_argument("processId",type=str,help="processId is needed")


def handleException(error):
        print("============== ERROR handleResponse ===============")
        print(error)
        errorStr=str(error)
        return Response(
            response=json.dumps({
                    "messge":"Bad Request",
                    "Error":errorStr
                    }),
            status=500,
            mimetype="application/json"
        )

class TransactionFilter(Resource):
    def get(self):
            args=transactionReqParser.parse_args()
            print(args)
            
            return {"message":"successfully TransactionFilter"}