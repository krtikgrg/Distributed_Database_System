import sys
import sqlparse

import config

from input import TakeInput
from trace import Logger
from query import Query

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

while(True):
    query = toInp.inputQuery()
    queries = sqlparse.split(query)

    for query in queries:
        sqlParsed = sqlparse.format(query, reindent=True, keyword_case='upper')
        sqlParsed = sqlParsed[:-1] # removing semi-colon here
        sqlParsed = sqlParsed.strip()

        config.debugPrint(sqlParsed)

        if sqlParsed == 'EXIT' or sqlParsed == 'quit':
            config.exitShell()

        config.parsedQuery = Query()
        config.parsedQuery.parse(sqlParsed)