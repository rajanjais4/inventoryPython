utilsRelativePath = "./utils"
welcomeJsonFileRelativePath = "./utils/welcome.json"

#########################  Mongo Config Details  ###############################
mongoUri = "mongodb+srv://inventory-admin:inventory123@inventory.rbcanbq.mongodb.net/test?authSource=admin&replicaSet=atlas-13oxx1-shard-0&readPreference=primary&ssl=true"
mongoInventoryDb = "raado"
mongoUserCollection = "raado-users"
mongoTransactionCollection = "raado-transactions"
######################### common Collection SDK ################################
id = "_id"
######################### raado-transaction Collection SDK #####################
tnxCollectionTimeOfTransaction = "timeOfTransaction"
tnxCollectionFromProcess = "fromProcess"
tnxCollectionToProcess = "toProcess"
tnxCollectionFromUserId = "fromUserId"
tnxCollectionToUserId = "toUserId"
tnxCollectionFromProcess = "fromProcess"
tnxCollectionFromUserWage="amount"
tnxCollectionFromUserName = "fromUserName"
txnCollectionStatus="status"
txnCollectionEntries="entries"

######################### raado-user Collection SDK #####################
userCollectionUserId = "userId"
userCollectionUserName="name"
######################### API Input Parameter #####################
userIdParameter = "userId"
startDateParameter = "startDate"
endDateParameter = "endDate"
processIdParameter = "processId"

######################### Data base constants #####################
DataBaseStatusApproved="APPROVED"

######################### Process Accounting Constants #################
processAccountingSchemaHeader = ["User Id","User Name","ProcessId","Total Wage"]
processAccountingEntitySend="entitySend"
processAccountingEntityReceived="entityReceived"
processAccountingUserIdWiseDetails="userIdWiseDetails"
processAccountingTotalWage="totalWage"
processAccountingFromUser="fromUserId"
processAccountingToUser="toUserId"
processAccountingStaticCsvPath="./src/static/processAccounting.csv"

######################### User Accounting Constants #################
userAccountingStaticCsvPath="./src/static/userAccounting.csv"

######################### Static Stock ##########################
staticStockUrl='http://ec2-44-204-192-171.compute-1.amazonaws.com:8888/staticResource/getGlobalStocks'
warehouse="WAREHOUSE"
data="data"
stockStaticCsvPath="./src/static/stockReport.csv"