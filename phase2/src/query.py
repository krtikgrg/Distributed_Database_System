import config
import sqlparse
from sql_metadata import Parser
class Query:
    '''
    An SQL query will be parsed further here, and broken to multiple parts like
    HAVING Clause, GROUP BY clause etc. All this data will be stored.
    '''
    def __init__(self):
        config.logger.log("Query::Constructor")
        pass

    def parse(self,query):
        '''
        Function to parse a query
        '''
        config.logger.log("Query::parse")

        parsed = sqlparse.parse(query)[0]
        print(parsed.tokens)
        print("TEMP")
        print(parsed)    

        #varables to be parsed
        self.relations = []
        self.join_conditions = {
            "relation1":[],
            "attribute1":[],
            "operator":[],
            "relation2":[],
            "attribute2":[]
        }
        self.select_conditions = {
            "relation":[],
            "attribute":[],
            "operator":[],
            "value":[]
        }
        self.all_projects = {
            "attribute":[],
            "relation":[]
        }
        self.aggregates = {
            "attribute":[],
            "relation":[],
            "operator":[]
        }
        self.group_by = {
            "attribute":[],
            "relation":[]
        }
        self.having_select = {
            "relation":[],
            "attribute":[],
            "operator":[],
            "value":[]
        }
        self.project = {
            "attribute":[],
            "relation":[]
        }
        self.PROJECT_ALL_ATTRIBUTES = None
        self.HAVING_CLAUSE_EXIST = None
        self.HAVE_AGGREGATES = None
        self.GROUP_BY_CLAUSE_EXIST = None
        self.PART_ONE_PROJECT_ALL = None
        self.SELECT_ALL = None

        # code to set/extract the above variable from the given query

