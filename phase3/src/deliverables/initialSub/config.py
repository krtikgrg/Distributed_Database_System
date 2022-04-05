DEBUG = 0
PATH_TO_LOGS_FILE = "./logs.txt"

logger = None
parsedQuery = None
aggregateOperators = ["AVG","COUNT","MAX","MIN","SUM"]
arithmeticOperators = ["=","!=","<",">","<=",">="]

#Assigning some random currently, will be changed later on
#Will be extracted using sql catalog by means of a utility function
relationColumnMap = {
    't1' : ['col2','a','c2','c4','c3'],
    't2' : ['col1','f','c5'],
    't3' : ['col4','col5','d','e'],
    't4' : ['b','c','col3']
}
joinSelectivities = {}
relationNumEntries = {}
globalTunnels = {}
globalConnections = {}
latencies = {}
transferCoefficients = {}
costProcessing = 1e-6
relationCellSizeMap = {}
catalogName = "zomato_catalog_outlaws"
paramikoConnections = {}
tempTables = {}
# relationColumnMap = {
#     'r1' : ['a','q','r','s','t'],
#     'r2' : ['b','l','m','n','o','p'],
#     'r3' : ['c','k'],
#     'r4' : ['d','i','j'],
#     'r5' : ['e','f','g','h']
# }

Tables = {
    'Name':['User','Restaurants','Food_Item','Ordre','Order_Items'],
    'Fragmentation_Type':['VF','VF','HF','DHF','DHF'],
    'Number_Of_Fragments':[2,2,3,3,3]
}
TableKeys = {
    'User':"PK_Custom",
    'Restaurants':"PK_Custom",
    'Food_Item':"PK_Custom",
    'Ordre' : "PK_Custom"
}
Columns = {
    'Table_Name': ['User','User','User','User','User','Restaurants','Restaurants','Restaurants','Restaurants','Restaurants','Restaurants','Restaurants','Food_Item','Food_Item','Food_Item','Food_Item','Food_Item','Food_Item','Ordre','Ordre','Ordre','Ordre','Order_Items','Order_Items','Order_Items'],
    'Column_Name': ['Name','Email','Address','Phone_Number','PK_Custom','Name','Address','Email','Rating','Specialty','Num_Reviews','PK_Custom','Name','Type','Price','Category','FK_Restaurant','PK_Custom','User_ID','Restaurant_ID','Amount','PK_Custom','Order_ID','Item_ID','Quantity']
}
Horizontal_Fragments = {
    'Fragment_Name' : ['Food_Item_Chinese','Food_Item_Indian','Food_Item_Italian'],
    'Table_Name' : ['Food_Item','Food_Item','Food_Item'],
    'Attribute' : ['Type','Type','Type'],
    'Operator' : ['=','=','='],
    'Val' : ['Chinese','Indian','Italian']
}
Vertical_Fragments = {
    'Fragment_Name' : ['Restaurants_Minimal','Restaurants_Remaining','User_Minimal','User_Remaining'],
    'Table_Name' : ['Restaurants','Restaurants','User','User']
}
VF_Columns = {
    'Fragment_Name':['Restaurants_Minimal','Restaurants_Minimal','Restaurants_Minimal','Restaurants_Minimal','Restaurants_Remaining','Restaurants_Remaining','Restaurants_Remaining','Restaurants_Remaining','User_Minimal','User_Minimal','User_Minimal','User_Remaining','User_Remaining','User_Remaining'],
    'Column_Name' : ['Name','Rating','Specialty','PK_Custom','PK_Custom','Address','Email','Num_Reviews','Name','Email','PK_Custom','Address','Phone_Number','PK_Custom']
}
Derived_Horizontal_Fragments = {
    'Table_Name':['Order_Items','Order_Items','Order_Items','Ordre','Ordre','Ordre'],
    'Fragment_Name':['Order_Items_Chinese','Order_Items_Indian','Order_Items_Italian','User_Restaurant_Order_Amount_Chinese','User_Restaurant_Order_Amount_Indian','User_Restaurant_Order_Amount_Italian'],
    'Horizontal_Fragment_Name':['Food_Item_Chinese','Food_Item_Indian','Food_Item_Italian','Order_Items_Chinese','Order_Items_Indian','Order_Items_Italian'],
    'Direct_Fragment':[1,1,1,0,0,0]
}
Sites = {
    'Site' : [1,2,3,4],
    'User_Name' : ["user","user","user","user"],
    'Password' : ["iiit123","iiit123","iiit123","iiit123"],
    'IP_Address' : ["10.3.5.215","10.3.5.214","10.3.5.213","10.3.5.212"]
}
Allocation = {
    'Fragment_Name' : ["Food_Item_Chinese","Food_Item_Indian","Food_Item_Italian","Restaurants_Minimal","Restaurants_Remaining","User_Minimal","User_Remaining","Order_Items_Chinese","Order_Items_Indian","Order_Items_Italian","User_Restaurant_Order_Amount_Chinese","User_Restaurant_Order_Amount_Indian","User_Restaurant_Order_Amount_Italian"],
    'Site' : [1,2,3,4,4,4,2,1,2,3,1,2,3]
}

def debugPrint(str):
    '''
    Function that helps to print debug statements when the code is run in debug mode.
    Accepts a string as input and prints it on stdout with appropriate prompts.
    '''
    global DEBUG
    global logger
    logger.log("config::debugPrint") 
    if DEBUG == 1:
        print("DEBUG ::",str)

def errorPrint(str):
    '''
    Function that helps to print error statements.
    '''
    global logger
    logger.log("config::errorPrint")
    print("ERROR ::",str)
    exit()

def exitShell():
    '''
    Function to exit the DDBMS shell
    '''
    global logger
    logger.log("config::exitShell")
    print("Exiting!!!")
    exit(0)