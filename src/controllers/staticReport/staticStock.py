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
import requests
import datetime 

class StockReport(Resource):
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
    def convertToCsv(self,staticStockDict):
        result=[]
        TimeStamp=datetime.datetime.now()
        result.append(["TimeStamp",TimeStamp])
        result.append(["Entity","Stock"])
        for entity in staticStockDict:
            result.append([entity,staticStockDict[entity]])
        my_df = pd.DataFrame(result)
        return my_df
    def saveCsvFile(self,csvResult,path):
        print("start saving data to csv file in static")
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        csvResult.to_csv(path,index=False,header=False)
    def makeLabelValueDict(self,staticStockLabelDict):
        dataDict=staticStockLabelDict["data"]
        result={}
        # print(dataDict)
        for key,entityList in dataDict.items():
            for entity in entityList:
                result[entity["value"]]=entity["label"]
        print(result)
        return result
    def updateLabel(self,staticStockDict,labelValueDict):
        result={}
        for key,value in staticStockDict.items():
            if key in labelValueDict:
                key=labelValueDict[key]
            result[key]=value
        return result

    def get(self):
        print("======= get stock =======")
        try:
            staticStockResponse = requests.get(constants.staticStockUrl)
            staticStockLabelResponse = requests.get(constants.staticStockLabelUrl)
            staticStockLabelDict={}
            labelValueDict={}
            if staticStockLabelResponse.ok:
                staticStockLabelDict=staticStockLabelResponse.json()
                labelValueDict=self.makeLabelValueDict(staticStockLabelDict)
            if staticStockResponse.ok:
                staticStockDict=staticStockResponse.json()[constants.data][constants.warehouse]
                staticStockDict=self.updateLabel(staticStockDict,labelValueDict)
                csvResult=self.convertToCsv(staticStockDict)
                # print(csvResult)
                response_stream = BytesIO(csvResult.to_csv(index=False,header=False).encode())
                self.saveCsvFile(csvResult,constants.stockStaticCsvPath)
                return send_file(
                        response_stream,
                        mimetype="text/csv",
                        attachment_filename="export.csv",
                    )
            else:
                pass

        except Exception as e:
            return self.handleException(e)