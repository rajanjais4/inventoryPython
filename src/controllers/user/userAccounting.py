from controllers.transaction.TransactionFilter import TransactionFilter
from controllers.user.userById import UserById
from ast import arguments
from lib2to3.pytree import convert
import constants
from flask_restful import Api, Resource, reqparse
from flask import Response
from mongoConnection import MongoConnection
import json
import sys
import pandas as pd
from io import BytesIO
from flask import send_file

sys.path.insert(0, '../..')


class UserAccounting(Resource):

    def _print(self,message):
        print("---------- start ------------")
        print(message)
        print("---------- end ------------")

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
            constants.startDateParameter, type=int, help="start date is needed for this request", required=True)
        userReqParser.add_argument(
            constants.endDateParameter, type=int, help="endDate date is needed for this request", required=True)
        userReqParser.add_argument(
            constants.userIdParameter, type=str, help="userId is needed", required=True)
        args = userReqParser.parse_args()
        return args
    def validateTransactionDict(self,transactionDict,userId):
        if (transactionDict[constants.tnxCollectionFromUserId] == userId and
            transactionDict[constants.txnCollectionStatus] == constants.DataBaseStatusApproved):
            return True
        return False;

    def getProcessedOuputByUser(self, transactionDictList, userId,userName):
        print("getProcessedOuputByUser")
        result={"userId": userId,"userName": userName,"processWisePayment":{}}
        processWisePayment={}
        for transactionDict in transactionDictList:
            if self.validateTransactionDict(transactionDict,userId) == True:
                process=transactionDict[constants.tnxCollectionFromProcess]
                processTxnWage=transactionDict[constants.tnxCollectionFromUserWage]
                if process in processWisePayment:
                    processWisePayment[process]+=processTxnWage
                else:
                    processWisePayment[process]=processTxnWage
        result["processWisePayment"]=processWisePayment
        self._print(result)
        return result
    def convertProcessedOuputByUserToCsv(self,dict):
        result=[["User Id","User Name","ProcessId","Total Wage"]]
        userId=dict["userId"]
        userName=dict["userName"]
        processWisePayment=dict["processWisePayment"]
        for processId in processWisePayment:
            totalWage=processWisePayment[processId]
            result.append([userId,userName,processId,totalWage])
        self._print(result)
        my_df = pd.DataFrame(result)
        return my_df

    def get(self):
        args = self.getArgs()
        try:
            transactionFilter = TransactionFilter()
            transactionFilterResponse = transactionFilter.get()
            if transactionFilterResponse.status_code == 200:
                uerById = UserById()
                userDetailsResponse = uerById.get()
                if userDetailsResponse.status_code == 200:
                    userDetailsDictList = json.loads(
                        (userDetailsResponse.response[0]))
                    transactionDictList = json.loads(
                        (transactionFilterResponse.response[0]))
                    processedOuputByUser = self.getProcessedOuputByUser(
                        transactionDictList, args[constants.userIdParameter],
                        userDetailsDictList[0][constants.userCollectionUserName])
                    csvResult=self.convertProcessedOuputByUserToCsv(processedOuputByUser)
                    response_stream = BytesIO(csvResult.to_csv(index=False,header=True).encode())
                    return send_file(
                        response_stream,
                        mimetype="text/csv",
                        attachment_filename="export.csv",
                    )
                    # return Response(
                    #     response=json.dumps(result),
                    #     status=200,
                    #     mimetype="application/json"
                    # )
        except Exception as e:
            return self.handleException(e)
