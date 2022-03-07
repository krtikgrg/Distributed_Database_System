DEBUG = 0
PATH_TO_LOGS_FILE = "./logs.txt"

logger = None
parsedQuery = None
aggregateOperators = ["AVG","COUNT","MAX","MIN","SUM"]
arithmeticOperators = ["=","!=","<",">","<=",">="]

#Assigning some random currently, will be changed later on
#Will be extracted using sql catalog by means of a utility function
# relationColumnMap = {
#     't1' : ['col2','a','c2','c4','c3'],
#     't2' : ['col1','f','c5'],
#     't3' : ['col4','col5','d','e'],
#     't4' : ['b','c','col3']
# }
relationColumnMap = {
    'r1' : ['a','q','r','s','t'],
    'r2' : ['b','l','m','n','o','p'],
    'r3' : ['c','k'],
    'r4' : ['d','i','j'],
    'r5' : ['e','f','g','h']
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