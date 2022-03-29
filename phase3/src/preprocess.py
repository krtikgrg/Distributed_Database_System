import config
import copy
import sshtunnel
from sshtunnel import SSHTunnelForwarder
import pymysql
import logging
import pandas as pd
import time
import paramiko

def createSSHTunnels():
    '''
    Function to create ssh tunnels as global variables for each of the sites
    '''
    config.logger.log("preprocess::createSSHTunnels")
    
    if config.DEBUG:
        sshtunnel.DEFAULT_LOGLEVEL = logging.DEBUG

    for i in range(len(config.Sites['Site'])):
        siteno = config.Sites['Site'][i]
        ip = config.Sites['IP_Address'][i]
        passw = config.Sites['Password'][i]
        uname = config.Sites['User_Name'][i]

        config.globalTunnels[siteno] = SSHTunnelForwarder(
            (ip,22),
            ssh_username=uname,
            ssh_password=passw,
            remote_bind_address=('127.0.0.1', 3306)
        )
        config.globalTunnels[siteno].start()

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(ip,port=22,username=uname,password=passw)
        config.paramikoConnections[siteno] = ssh
        (a,b,c) = ssh.exec_command('ls')
        op = b.read()
        config.debugPrint(str(op))


def createMySqlConnections():
    '''
    Function to create mysql connections using ssh tunnels with our sites
    '''
    config.logger.log("preprocess::createMySqlConnections")

    for x in config.globalTunnels:
        config.globalConnections[x] = pymysql.connect(
            host='127.0.0.1',
            user='user',
            passwd='iiit123',
            db='zomato_catalog_outlaws',
            port=config.globalTunnels[x].local_bind_port
        )

def closeConnections():
    '''
    Function to close the ssh tunnels and the mysql connections
    '''
    config.logger.log("preprocess::closeConnetions")

    for x in config.globalTunnels:
        config.globalConnections[x].close()
        config.globalTunnels[x].close()
        config.paramikoConnections[x].close()

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
    rels = copy.deepcopy(list(config.relationColumnMap.keys()))
    for i in range(len(rels)):
        for j in range(len(rels)):
            config.joinSelectivities[(rels[i],rels[j])] = 1

    #if input is being taken then take it now and update the ones for which you get an input
    #pending

def getRelationLengths():
    '''
    Function to scan relation length using ssh and sql, we will get sizes of frags and then add them to get actual relation sizes
    '''
    config.logger.log('preprocess::getRelationLengths')
    
    sql = "select distinct table_rows from information_schema.TABLES where TABLE_NAME = '"
    
    for i in range(len(config.Allocation['Fragment_Name'])):
        frag_name = config.Allocation['Fragment_Name'][i]
        siteno = config.Allocation['Site'][i]

        strt = time.time()
        sz = pd.read_sql_query(sql+frag_name+"';",config.globalConnections[siteno])
        end = time.time()
        if siteno not in config.latencies:
            config.latencies[siteno] = []
        config.latencies[siteno].append(end-strt)

        sz = sz.iloc[0][0]
        config.relationNumEntries[frag_name] = sz

    for i in range(len(config.Horizontal_Fragments['Table_Name'])):
        frag_name = config.Horizontal_Fragments['Fragment_Name'][i]
        tab_name = config.Horizontal_Fragments['Table_Name'][i]

        if tab_name not in config.relationNumEntries:
            config.relationNumEntries[tab_name] = 0
        
        config.relationNumEntries[tab_name] += config.relationNumEntries[frag_name]
    
    for i in range(len(config.Vertical_Fragments['Table_Name'])):
        frag_name = config.Vertical_Fragments['Fragment_Name'][i]
        tab_name = config.Vertical_Fragments['Table_Name'][i]

        if tab_name not in config.relationNumEntries:
            config.relationNumEntries[tab_name] = config.relationNumEntries[frag_name]

    for i in range(len(config.Derived_Horizontal_Fragments['Table_Name'])):
        frag_name = config.Derived_Horizontal_Fragments['Fragment_Name'][i]
        tab_name = config.Derived_Horizontal_Fragments['Table_Name'][i]

        if tab_name not in config.relationNumEntries:
            config.relationNumEntries[tab_name] = 0
        
        config.relationNumEntries[tab_name] += config.relationNumEntries[frag_name]

    for x in config.relationNumEntries:
        config.debugPrint(x+" "+str(config.relationNumEntries[x]))
    
def getEntrySizes():
    '''
    Function which will execute sql commands to get eah cell size and entry size for all the tables
    '''
    config.logger.log("preprocess::getEntrySizes")
    
    sql = "select distinct column_name,data_type,character_maximum_length from information_schema.COLUMNS WHERE TABLE_NAME = '"
    mper = {}
    for i in range(len(config.Allocation['Fragment_Name'])):
        frag_name = config.Allocation['Fragment_Name'][i]
        siteno = config.Allocation['Site'][i]

        sz = pd.read_sql_query(sql+frag_name+"';",config.globalConnections[siteno])
        # print(list(sz.columns))
        cols = sz['COLUMN_NAME']
        datype = sz['DATA_TYPE']
        sszz = sz['CHARACTER_MAXIMUM_LENGTH']
        
        mper[frag_name] = {}
        for j in range(len(datype)):
            if datype[j] == 'varchar':
                mper[frag_name][cols[j]] = int(sszz[j])
            elif datype[j] == 'int':
                mper[frag_name][cols[j]] = 4
            else:
                mper[frag_name][cols[j]] = 8
    
    for i in range(len(config.Horizontal_Fragments['Fragment_Name'])):
        frag_name = config.Horizontal_Fragments['Fragment_Name'][i]
        tab_name = config.Horizontal_Fragments['Table_Name'][i]

        if tab_name not in config.relationCellSizeMap:
            config.relationCellSizeMap[tab_name] = {}
            for x in mper[frag_name]:
                config.relationCellSizeMap[tab_name][x] = mper[frag_name][x]
        
    for i in range(len(config.Vertical_Fragments['Fragment_Name'])):
        frag_name = config.Vertical_Fragments['Fragment_Name'][i]
        tab_name = config.Vertical_Fragments['Table_Name'][i]

        if tab_name not in config.relationCellSizeMap:
            config.relationCellSizeMap[tab_name] = {}
        for x in mper[frag_name]:
            config.relationCellSizeMap[tab_name][x] = mper[frag_name][x]

    for i in range(len(config.Derived_Horizontal_Fragments['Fragment_Name'])):
        frag_name = config.Derived_Horizontal_Fragments['Fragment_Name'][i]
        tab_name = config.Derived_Horizontal_Fragments['Table_Name'][i]

        if tab_name not in config.relationCellSizeMap:
            config.relationCellSizeMap[tab_name] = {}
            for x in mper[frag_name]:
                config.relationCellSizeMap[tab_name][x] = mper[frag_name][x]
    
    for x in config.relationColumnMap:
        if x not in config.relationCellSizeMap:
            config.relationCellSizeMap[x] = copy.deepcopy(mper[x])

    config.debugPrint(config.relationCellSizeMap)

def computeTransferCoefficients():
    '''
    Function to compute the transfer cost for each site using the latencies that were present while retrieving the sql result
    '''
    config.logger.log('preprocess::computeTransferCoefficients')

    for x in config.latencies:
        summ = 0
        for y in config.latencies[x]:
            summ += y
        summ /= len(config.latencies[x])
        config.transferCoefficients[x] = summ

def deleteTempFilesTables():
    '''
    Function to delete the temporary files and tables which were created along the execution of the command
    '''
    config.logger.log("preprocess::deleteTempFilesTables")
    #temp file is only dump.txt

    command = "rm ./Outlaws/dump.txt"
    for x in config.paramikoConnections:
        config.paramikoConnections[x].exec_command(command)

    for x in config.tempTables:
        tab_name = x
        siteno = config.tempTables[x]

        sqlQuery = "drop table "+config.catalogName+"."+tab_name+";"
        cur = config.globalConnections[siteno].cursor()
        cur.execute(sqlQuery)
        config.globalConnections[siteno].commit()