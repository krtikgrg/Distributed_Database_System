import config
import sqlparse
import copy
from sql_metadata import Parser
class Query:
    '''
    An SQL query will be parsed further here, and broken to multiple parts like
    HAVING Clause, GROUP BY clause etc. All this data will be stored.
    '''
    def __init__(self):
        config.logger.log("Query::Constructor")
        pass

    def getAttrRelAoper(self,col):
        '''
        Function to extract the relation, attribute and aggregate operator specified in col
        '''
        config.logger.log("Query::getAttrRelAoper")

        attr = ""
        rel = ""
        aoper = ""
        haveaggr = 0
        if col.find('(') != -1:
            #aggregate operator present
            self.HAVE_AGGREGATES = 1
            haveaggr = 1
            opername = col[:col.find('(')].upper()
            if opername not in config.aggregateOperators:
                config.errorPrint("Aggregate Operator = "+opername+" Not Found")
            else:
                aoper = opername
            col = col[col.find('(')+1:col.find(')')]

        if col.find('.') != -1:
            #column specified as rel.attribute currently
            col = col.split('.')
            rel = col[0]
            if rel not in self.relations:
                config.errorPrint("Found a relation in SELECT which is not present in FROM")
            attr = col[1]
            #######check if attr is a part of rel
        else:
            #######rel to be extracted from table data
            #######then chack if that rel present in self.relations
            #######giving general value as "TO_BE_EXTRACTED for now"
            rel = "TO_BE_EXTRACTED"
            attr = col

        if haveaggr == 1:
            self.aggregates['attribute'].append(attr)
            self.aggregates['relation'].append(rel)
            self.aggregates['operator'].append(aoper)
        return attr,rel,aoper

    def parse(self,query):
        '''
        Function to parse a query
        '''
        config.logger.log("Query::parse")

        query = query.splitlines()
        for i in range(len(query)):
            query[i] = query[i].split()

        #varables to be parsed
        self.relations = [] #done from "FROM" clause
        self.join_conditions = {
            "relation1":[],
            "attribute1":[],
            "operator":[],
            "relation2":[],
            "attribute2":[]
        } # from where clause
        self.all_projects = {
            "attribute":[],
            "relation":[],
            "aggregate_operator":[]
        } #DONE from slect, DONE from group by, from having
        self.aggregates = {
            "attribute":[],
            "relation":[],
            "operator":[]
        } #done from select cols, having clause
        self.group_by = {
            "attribute":[],
            "relation":[]
        } # DONE from group by

        # to extend support to AND and OR keywords, we will maintain a list of
        # below provided dictionary structure. Where each element in the list
        # will be a separate condition specified by using ORs and all the elements
        # are specified using ANDs. 
        self.select_conditions = []     # from where clause
        selectStructure = {
            "relation":[],
            "attribute":[],
            "operator":[],
            "value":[]
        } 
        self.having_select = []     # from having clause
        self.project = {
            "attribute":[],
            "relation":[],
            "aggregate_operator":[]
        } #partially done from select
        self.PROJECT_ALL_ATTRIBUTES = None #DONE
        self.HAVING_CLAUSE_EXIST = None #DONE
        self.HAVE_AGGREGATES = None #DONE from select, from having
        self.GROUP_BY_CLAUSE_EXIST = None #DONE
        self.PART_ONE_PROJECT_ALL = None #DONE
        self.SELECT_ALL = None #DONE

        # code to set/extract the above variable from the given query
        
        # First Extracting all the relations that we need
        # extracting from "FROM" Keyword
        itr = 0
        while(True):
            if query[itr][0] == "FROM":
                break
            else:
                itr += 1
        run = 1
        while(run):
            if query[itr][-1][-1] != ',':
                run = 0
            else:
                query[itr][-1] = query[itr][-1][:-1]
            self.relations.append(query[itr][-1])
            itr += 1

        #Now lets extract columns from select keyword
        #iterator variable
        itr = 0
        if query[0][1] == "*":
            self.PROJECT_ALL_ATTRIBUTES = 1
        else:
            self.PROJECT_ALL_ATTRIBUTES = 0
            
            run = 1
            while(run):
                if query[itr][-1][-1] != ',':
                    run = 0
                else:
                    query[itr][-1] = query[itr][-1][:-1]
                attr,rel,aoper = self.getAttrRelAoper(query[itr][-1])
                self.project["attribute"].append(attr)
                self.project["relation"].append(rel)
                self.project['aggregate_operator'].append(aoper)
                itr += 1

            self.all_projects = copy.deepcopy(self.project)
        
        #processing group bys first
        itr = 0
        while(itr<len(query)):
            if query[itr][0] == "GROUP":
                self.GROUP_BY_CLAUSE_EXIST = 1
                break
            itr += 1
        if itr == len(query):
            self.GROUP_BY_CLAUSE_EXIST = 0

        if self.GROUP_BY_CLAUSE_EXIST == 1:
            run = 1
            while(run):
                if query[itr][-1][-1] != ',':
                    run = 0
                else:
                    query[itr][-1] = query[itr][-1][:-1]
                attr,rel,aoper = self.getAttrRelAoper(query[itr][-1])
                self.all_projects["attribute"].append(attr)
                self.all_projects["relation"].append(rel)
                self.all_projects['aggregate_operator'].append(aoper)

                self.group_by['attribute'].append(attr)
                self.group_by['relation'].append(rel)
                itr += 1

        if self.GROUP_BY_CLAUSE_EXIST == 0 and self.HAVING_CLAUSE_EXIST == 0 and self.PROJECT_ALL_ATTRIBUTES == 1:
            self.PART_ONE_PROJECT_ALL = 1
        else:
            self.PART_ONE_PROJECT_ALL = 0

        #processing having and where are same
        #checking if having clause and where clause exist
        itr = 0
        while(itr<len(query)):
            if query[itr][0] == "HAVING":
                self.HAVING_CLAUSE_EXIST = 1
                break
            itr += 1
        if itr == len(query):
            self.HAVING_CLAUSE_EXIST = 0

        itr = 0
        while(itr<len(query)):
            if query[itr][0] == "WHERE":
                self.SELECT_ALL = 0
                break
            itr += 1
        if itr == len(query):
            self.SELECT_ALL = 1