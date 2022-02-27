DEBUG = 0
PATH_TO_LOGS_FILE = "./logs.txt"

logger = None
parsedQuery = None

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

def exitShell():
    '''
    Function to exit the DDBMS shell
    '''
    global logger
    logger.log("config::exitShell")
    print("Exiting!!!")
    exit(0)