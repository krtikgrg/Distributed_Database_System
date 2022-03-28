import config
import copy

def getSchema(toInp):
    '''
    function to take sql statements as input which
    will describe the schema of the application database
    at hand
    '''
    config.logger.log("preprocess::getSchema")
    toInp.inputSchema()

def generateRelationColumnMapFromMetaData():
    '''
    Function to generate the relationColumnMap from the read metadata through csv/sql
    csv/sql reading is yet to be done
    '''
    config.logger.log("preprocess::generateRelationColumnMapFromMetaData")
    config.relationColumnMap = {}
    for i in range(len(config.Columns['Table_Name'])):
        if config.Columns['Table_Name'][i] not in config.relationColumnMap:
            config.relationColumnMap[config.Columns['Table_Name'][i]] = []
        config.relationColumnMap[config.Columns['Table_Name'][i]].append(config.Columns['Column_Name'][i])

def initializeJoinSelectivities():
    '''
    Function to initialize the join selectivities as 1 initially
    if we are supposed to maintain these values then i will add update
    routines which will get called once a query is executed and the
    values from the execution will update these selectivities accordingly
    else if a file is given then we will take them as input from that file
    and for the pairs for which it will not be given, the value will be set to 1 as default
    '''

    config.logger.log("preprocess::initializeJoinSelectivities")

    config.joinSelectivities = {}
    rels = copy.deepcopy(config.relationColumnMap.keys())
    for i in range(len(rels)):
        for j in range(len(rels)):
            config.joinSelectivities[(rels[i],rels[j])] = 1

    #if input is being taken then take it now and update the ones for which you get an input
    #pending

def getRelationSizes():
    '''
    Function to scan relation size using ssh and sql, we will get sizes of frags and then add them to get actual relation sizes
    '''
    config.logger.log('preprocess::getRelationSizes')
    #pending
    
    #TEMPORARY
    config.relationSizes = {}
    for x in config.relationColumnMap:
        config.relationSizes[x] = 10
