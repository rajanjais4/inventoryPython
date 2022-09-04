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
import os

sys.path.insert(0, '../..')


class UserAccounting(Resource):

    def _print(self,message):
        pass
        # print("---------- start ------------")
        # print(message)
        # print("---------- end ------------")

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
        if transactionDict[constants.txnCollectionStatus] == constants.DataBaseStatusApproved:
            return True
        return False;
    def validateFromUserIdTransactionDict(self,transactionDict,userId):
        if (transactionDict[constants.processAccountingFromUser] == userId and
            transactionDict[constants.txnCollectionStatus] == constants.DataBaseStatusApproved):
            return True
        return False;
    def validateToUserIdTransactionDict(self,transactionDict,userId):
        if (transactionDict[constants.processAccountingToUser] == userId and
            transactionDict[constants.txnCollectionStatus] == constants.DataBaseStatusApproved):
            return True
        return False;
    def saveCsvFile(self,csvResult,path):
        print("start saving data to csv file in static")
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        csvResult.to_csv(path,index=False,header=False)

    def getProcessedOuputByUser(self, transactionDictList, userId,userName):
        print("getProcessedOuputByUser")
        result={"userId": userId,"userName": userName,"processWisePayment":{}}
        processWisePayment={}
        for transactionDict in transactionDictList:
            if self.validateTransactionDict(transactionDict,userId) == True:
                process=transactionDict[constants.tnxCollectionFromProcess]
                processTxnWage=0
                entitySend={}
                entityReceived={}

                if self.validateFromUserIdTransactionDict(transactionDict,userId) == True:
                    processTxnWage=transactionDict[constants.tnxCollectionFromUserWage]
                    entitySend=transactionDict[constants.txnCollectionEntries]
                if self.validateToUserIdTransactionDict(transactionDict,userId) == True:
                    entityReceived=transactionDict[constants.txnCollectionEntries]

                if process in processWisePayment:
                    processWisePayment[process][constants.processAccountingTotalWage]+=processTxnWage

                    # update entity send
                    entitySendTotal=processWisePayment[process][constants.processAccountingEntitySend]
                    for entity in entitySend:
                        if entity in entitySendTotal:
                            entitySendTotal[entity]+=entitySend[entity]
                        else:
                            entitySendTotal[entity]=entitySend[entity]
                    
                    # update entity Received
                    entityReceivedTotal=processWisePayment[process][constants.processAccountingEntityReceived]
                    for entity in entityReceived:
                        if entity in entityReceivedTotal:
                            entityReceivedTotal[entity]+=entityReceived[entity]
                        else:
                            entityReceivedTotal[entity]=entityReceived[entity]
                else:
                    processWisePayment[process]={
                        constants.processAccountingTotalWage:processTxnWage,
                        constants.processAccountingEntitySend:entitySend,
                        constants.processAccountingEntityReceived:entityReceived
                        }
        result["processWisePayment"]=processWisePayment
        self._print(result)
        return result
    # Get list of all received entity in the dict to update the header
    def getReceivedEntityList(self,dict):
        result=set()
        processWisePayment=dict["processWisePayment"]
        for processId in processWisePayment:
            result.update(processWisePayment[processId][constants.processAccountingEntityReceived].keys())
        return list(result)
    # Get list of all send entity in the dict to update the header
    def getSendEntityList(self,dict):
        result=set()
        processWisePayment=dict["processWisePayment"]
        for processId in processWisePayment:
            result.update(processWisePayment[processId][constants.processAccountingEntitySend].keys())
        return list(result)
    
    def updateHeader(self,entityList,suffix):
        result=[]
        for entity in entityList:
            result.append(entity+" "+suffix)
        return result
    

    def updateRowDataForEntity(self,entityDict,entityList):
        result=[]
        for entity in entityList:
            if entity in entityDict:
                result.append(entityDict[entity])
            else:
                result.append(0)
        return result
    
    def convertProcessedOuputByUserToCsv(self,dict):
        header=constants.processAccountingSchemaHeader.copy()
        # Get list of all received entity in the dict to update the header
        receivedEntityList=self.getReceivedEntityList(dict)
        sendEntityList=self.getSendEntityList(dict)
        # updating header for send entity with send suffix
        header.extend(self.updateHeader(sendEntityList,"send"))
        # updating header for received entity with received suffix
        header.extend(self.updateHeader(receivedEntityList,"received"))
        self._print(header)

        result=[header]
        userId=dict["userId"]
        userName=dict["userName"]
        processWisePayment=dict["processWisePayment"]
        for processId in processWisePayment:
            totalWage=processWisePayment[processId][constants.processAccountingTotalWage]
            row=[userId,userName,processId,totalWage]

            row.extend(
                (self.updateRowDataForEntity(processWisePayment[processId]
                [constants.processAccountingEntitySend],
                sendEntityList)
            ))

            row.extend(
                (self.updateRowDataForEntity(processWisePayment[processId]
                [constants.processAccountingEntityReceived],
                receivedEntityList)
            ))
            result.append(row)
        self._print(result)
        my_df = pd.DataFrame(result)
        return my_df

    def post(self):
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
                    response_stream = BytesIO(csvResult.to_csv(index=False,header=False).encode())
                    self.saveCsvFile(csvResult,constants.userAccountingStaticCsvPath)
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
