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


class ProcessAccounting(Resource):

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
            constants.processIdParameter, type=str, help="processId is needed", required=True)
        args = userReqParser.parse_args()
        return args
    
    def validateFromProcessIdTransactionDict(self,transactionDict,processId):
        if (transactionDict[constants.tnxCollectionFromProcess] == processId and
            transactionDict[constants.txnCollectionStatus] == constants.DataBaseStatusApproved):
            return True
        return False;
    def validateToProcessIdTransactionDict(self,transactionDict,processId):
        if (transactionDict[constants.tnxCollectionToProcess] == processId and
            transactionDict[constants.txnCollectionStatus] == constants.DataBaseStatusApproved):
            return True
        return False;

    def getProcessedOuputByUser(self, transactionDictList, processId):
        print("getProcessedOuputByUser")
        result={"processId": processId,"userIdWiseDetails":{}}
        userIdWiseDetails={}
        for transactionDict in transactionDictList:
            if transactionDict[constants.txnCollectionStatus] == constants.DataBaseStatusApproved:
                
                userId=transactionDict[constants.tnxCollectionToUserId]
                userName=transactionDict["fromUserName"]
                processTxnWage=0
                totalWagePaid=0
                entitySend={}
                entityReceived={}

                if self.validateFromProcessIdTransactionDict(transactionDict,processId) == True:
                    processTxnWage=transactionDict[constants.tnxCollectionFromUserWage]
                    entitySend=transactionDict[constants.txnCollectionEntries]
                if self.validateToProcessIdTransactionDict(transactionDict,processId) == True:
                    entityReceived=transactionDict[constants.txnCollectionEntries]
                
                # update userIdWiseDetails dict
                if userId in userIdWiseDetails:
                    # update total wage
                    userIdWiseDetails[userId]["totalWage"]+=processTxnWage
                    
                    # update entity send
                    entitySendTotal=userIdWiseDetails[userId]["entitySend"]
                    for entity in entitySend:
                        if entity in entitySendTotal:
                            entitySendTotal[entity]+=entitySend[entity]
                        else:
                            entitySendTotal[entity]=entitySend[entity]
                    
                    # update entity Received
                    entityReceivedTotal=userIdWiseDetails[userId]["entityReceived"]
                    for entity in entityReceived:
                        if entity in entityReceivedTotal:
                            entityReceivedTotal[entity]+=entityReceived[entity]
                        else:
                            entityReceivedTotal[entity]=entityReceived[entity]
                else:
                    userIdWiseDetails[userId]={
                        "userName":userName,
                        "totalWage":processTxnWage,
                        "entitySend":entitySend,
                        "entityReceived":entityReceived
                    }
        result["userIdWiseDetails"]=userIdWiseDetails
        self._print(result)
        return result
    # Get list of all received entity in the dict to update the header
    def getReceivedEntityList(self,dict):
        result=set()
        userIdWiseDetails=dict["userIdWiseDetails"]
        for userId in userIdWiseDetails:
            result.update(userIdWiseDetails[userId][constants.processAccountingEntityReceived].keys())
        return list(result)
    # Get list of all send entity in the dict to update the header
    def getSendEntityList(self,dict):
        result=set()
        userIdWiseDetails=dict["userIdWiseDetails"]
        for userId in userIdWiseDetails:
            result.update(userIdWiseDetails[userId][constants.processAccountingEntitySend].keys())
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
        processId=dict["processId"]
        userIdWiseDetails=dict["userIdWiseDetails"]
        for userId in userIdWiseDetails:
            userName=userIdWiseDetails[userId]["userName"]
            totalWage=userIdWiseDetails[userId]["totalWage"]
            row=[userId,userName,processId,totalWage]
            row.extend(
                (self.updateRowDataForEntity(userIdWiseDetails[userId]
                [constants.processAccountingEntitySend],
                sendEntityList)
            ))

            row.extend(
                (self.updateRowDataForEntity(userIdWiseDetails[userId]
                [constants.processAccountingEntityReceived],
                receivedEntityList)
            ))

            result.append(row)
        self._print(result)
        my_df = pd.DataFrame(result)
        return my_df

    def get(self):
        args = self.getArgs()
        try:
            transactionFilter = TransactionFilter()
            transactionFilterResponse = transactionFilter.get()
            if transactionFilterResponse.status_code == 200:
                    transactionDictList = json.loads(
                        (transactionFilterResponse.response[0]))
                    processedOuputByUser = self.getProcessedOuputByUser(
                        transactionDictList, args[constants.processIdParameter])
                    csvResult=self.convertProcessedOuputByUserToCsv(processedOuputByUser)
                    response_stream = BytesIO(csvResult.to_csv(index=False,header=True).encode())
                    return send_file(
                        response_stream,
                        mimetype="text/csv",
                        attachment_filename="export.csv",
                    )
                    # return Response(
                    #     response=json.dumps(processedOuputByUser),
                    #     status=200,
                    #     mimetype="application/json"
                    # )
        except Exception as e:
            return self.handleException(e)
