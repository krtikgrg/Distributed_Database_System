import sys
import sqlparse

import config

import time
from utility import copyFromServer, copyToServer, dumpTable, importTable
from input import TakeInput
from trace import Logger
from query import Query
from preprocess import generateRelationColumnMapFromMetaData, initializeJoinSelectivities, getSchema, getRelationLengths, createSSHTunnels, createMySqlConnections, closeConnections, computeTransferCoefficients, getEntrySizes, deleteTempFilesTables

# Checking if code has been run in DEBUG mode
n = len(sys.argv)
if n > 2:
    print("ERROR :: Unknown Number of Arguments")
    exit()
elif n == 2:
    if sys.argv[1] == '-d':
        config.DEBUG = 1

config.logger = Logger()
toInp = TakeInput()
getSchema(toInp)
generateRelationColumnMapFromMetaData()
initializeJoinSelectivities()
createSSHTunnels()
createMySqlConnections()
getRelationLengths()
computeTransferCoefficients()
getEntrySizes()

while(True):
    query = toInp.inputQuery()
    queries = sqlparse.split(query)

    for query in queries:
        STRT = time.time()
        sqlParsed = sqlparse.format(query, reindent=True, keyword_case='upper')
        sqlParsed = sqlParsed[:-1] # removing semi-colon here
        sqlParsed = sqlParsed.strip()

        config.debugPrint(sqlParsed)

        if sqlParsed == 'EXIT' or sqlParsed == 'quit':
            deleteTempFilesTables()
            closeConnections()
            config.exitShell()

        config.parsedQuery = Query()
        config.parsedQuery.parse(sqlParsed)

        config.parsedQuery.generateTree()
        # config.parsedQuery.PrintTree('./original.md')
        config.parsedQuery.optimizeTreeSelection()
        # config.parsedQuery.PrintTree('./selection_optimized.md')
        config.parsedQuery.optimizeTreeProjection() 
        # config.parsedQuery.PrintTree('./optimized.md') 
        config.parsedQuery.replaceRelationsWithFragments()
        # config.parsedQuery.PrintTree('./fragmented.md')
        config.parsedQuery.pushSelectsFragmented()
        if config.parsedQuery.emptyResult == 1:
            continue
        # config.parsedQuery.PrintTree('./fragmented_select.md')

        config.parsedQuery.pushProjectsFragmented()
        config.parsedQuery.PrintTree('./complete.md')
        config.parsedQuery.execute()
        END = time.time()
        print("Time Taken (In Seconds):",END-STRT)
        deleteTempFilesTables()