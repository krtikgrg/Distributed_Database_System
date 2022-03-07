import config
import sqlparse
import copy
from sql_metadata import Parser
from node import Node,ProjectNode,SelectNode,AggregateNode,JoinNode,UnionNode,RelationNode,HavingNode
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
            rel = None
            for x in config.relationColumnMap:
                if col in config.relationColumnMap[x]:
                    rel = x
                    break
            if rel is None:
                config.errorPrint("No relation contained a specified column "+col)
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
        config.logger.log("Parse::Initialising variables to be parsed")
        self.relations = []
        self.join_conditions = {
            "relation1":[],
            "attribute1":[],
            "operator":[],
            "relation2":[],
            "attribute2":[]
        }
        self.all_projects = {
            "attribute":[],
            "relation":[],
            "aggregate_operator":[]
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

        # to extend support to AND and OR keywords, we will maintain a list of
        # below provided dictionary structure. Where each element in the list
        # will be a separate condition specified by using ORs and all the elements
        # are specified using ANDs. 
        self.select_conditions = [] 
        selectStructure = {
            "relation":[],
            "attribute":[],
            "operator":[],
            "value":[]
        } 
        self.having_select = [] 
        havingStructure = {
            "aggregate_operator":[],
            "relation":[],
            "attribute":[],
            "operator":[],
            "value":[]
        }
        self.project = {
            "attribute":[],
            "relation":[],
            "aggregate_operator":[]
        } 
        self.PROJECT_ALL_ATTRIBUTES = None
        self.HAVING_CLAUSE_EXIST = None 
        self.HAVE_AGGREGATES = None
        self.GROUP_BY_CLAUSE_EXIST = None 
        self.PART_ONE_PROJECT_ALL = None 
        self.SELECT_ALL = None 
        self.HAVE_JOIN = None

        # code to set/extract the above variables from the given query
        
        # First Extracting all the relations that we need
        # extracting from "FROM" Keyword
        config.logger.log("Parse::Processing FROM clause")
        itr = 0
        while(True):
            if query[itr][0] == "FROM":
                break
            else:
                itr += 1
        run = 1
        while(itr<len(query) and run):
            if query[itr][-1][-1] != ',':
                run = 0
            else:
                query[itr][-1] = query[itr][-1][:-1]
            self.relations.append(query[itr][-1])
            itr += 1

        #Now lets extract columns from select keyword
        config.logger.log("Parse::Processing SELECT clause")
        #iterator variable
        itr = 0
        if query[0][1] == "*":
            self.PROJECT_ALL_ATTRIBUTES = 1
        else:
            self.PROJECT_ALL_ATTRIBUTES = 0
            
            run = 1
            while(itr<len(query) and run):
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
        
        #processing group bys now
        config.logger.log("Parse::Processing GROUP BY clause")
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
            while(itr<len(query) and run):
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

        #processing having and where are kind of similar
        #checking if having clause exists
        config.logger.log("Parse::Processing HAVING clause")
        itr = 0
        while(itr<len(query)):
            if query[itr][0] == "HAVING":
                self.HAVING_CLAUSE_EXIST = 1
                break
            itr += 1
        if itr == len(query):
            self.HAVING_CLAUSE_EXIST = 0

        if self.GROUP_BY_CLAUSE_EXIST == 0 and self.HAVING_CLAUSE_EXIST == 0 and self.PROJECT_ALL_ATTRIBUTES == 1:
            self.PART_ONE_PROJECT_ALL = 1
        else:
            self.PART_ONE_PROJECT_ALL = 0

        #if exists then processing it
        if self.HAVING_CLAUSE_EXIST == 1:
            #Assuming that having clause will only come with aggregates
            self.HAVE_AGGREGATES = 1
            while(itr<len(query)):
                if (query[itr][0] == "HAVING") or (query[itr][0] == "AND"):
                    #create new instance
                    instance = copy.deepcopy(havingStructure)
                    self.having_select.append(instance)
                
                if query[itr][1][0] == '(':
                    query[itr][1] = query[itr][1][1:]
                if query[itr][1][-1] == ')':
                    query[itr][1] = query[itr][1][:-1]
                
                value = 0
                operator = ""
                toProcess = ""
                if query[itr][1].find("!=") != -1:
                    index = query[itr][1].find("!=")
                    toProcess = query[itr][1][:index]
                    value = int(query[itr][1][index+2:])
                    operator = "!="
                elif query[itr][1].find("<=") != -1:
                    index = query[itr][1].find("<=")
                    toProcess = query[itr][1][:index]
                    value = int(query[itr][1][index+2:])
                    operator = "<="
                elif query[itr][1].find(">=") != -1:
                    index = query[itr][1].find(">=")
                    toProcess = query[itr][1][:index]
                    value = int(query[itr][1][index+2:])
                    operator = ">="
                elif query[itr][1].find("<") != -1:
                    index = query[itr][1].find("<")
                    toProcess = query[itr][1][:index]
                    value = int(query[itr][1][index+1:])
                    operator = "<"
                elif query[itr][1].find(">") != -1:
                    index = query[itr][1].find(">")
                    toProcess = query[itr][1][:index]
                    value = int(query[itr][1][index+1:])
                    operator = ">"
                elif query[itr][1].find("=") != -1:
                    index = query[itr][1].find("=")
                    toProcess = query[itr][1][:index]
                    value = int(query[itr][1][index+1:])
                    operator = "="
                else:
                    config.errorPrint("Operator not recognised in HAVING clause")
                attr,rel,aoper = self.getAttrRelAoper(toProcess)

                self.having_select[-1]['aggregate_operator'].append(aoper)
                self.having_select[-1]['relation'].append(rel)
                self.having_select[-1]['attribute'].append(attr)
                self.having_select[-1]['operator'].append(operator)
                self.having_select[-1]['value'].append(value)

                self.all_projects["attribute"].append(attr)
                self.all_projects["relation"].append(rel)
                self.all_projects['aggregate_operator'].append(aoper)

                itr += 1

        #checking if WHERE clause exists
        config.logger.log("Parse::Processing WHERE clause")
        itr = 0
        while(itr<len(query)):
            if query[itr][0] == "WHERE":
                self.SELECT_ALL = 0
                break
            itr += 1
        if itr == len(query):
            self.SELECT_ALL = 1
        
        #if exists then processing it
        if self.SELECT_ALL == 0:
            while(itr<len(query) and ((query[itr][0] == "WHERE") or (query[itr][0] == "AND") or (query[itr][0] == "OR"))):
                if (query[itr][0] == "WHERE") or (query[itr][0] == "AND"):
                    #create new instance
                    instance = copy.deepcopy(selectStructure)
                    if len(self.select_conditions) > 0:
                        if len(self.select_conditions[-1]['relation'])!=0:
                            self.select_conditions.append(instance)
                    else:
                        self.select_conditions.append(instance)

                if query[itr][1][0] == '(':
                    query[itr][1] = query[itr][1][1:]
                if query[itr][1][-1] == ')':
                    query[itr][1] = query[itr][1][:-1]

                operator = ""
                toProcess = ""
                remaining = ""
                if query[itr][1].find("!=") != -1:
                    index = query[itr][1].find("!=")
                    toProcess = query[itr][1][:index]
                    remaining = query[itr][1][index+2:]
                    operator = "!="
                elif query[itr][1].find("<=") != -1:
                    index = query[itr][1].find("<=")
                    toProcess = query[itr][1][:index]
                    remaining = query[itr][1][index+2:]
                    operator = "<="
                elif query[itr][1].find(">=") != -1:
                    index = query[itr][1].find(">=")
                    toProcess = query[itr][1][:index]
                    remaining = query[itr][1][index+2:]
                    operator = ">="
                elif query[itr][1].find("<") != -1:
                    index = query[itr][1].find("<")
                    toProcess = query[itr][1][:index]
                    remaining = query[itr][1][index+1:]
                    operator = "<"
                elif query[itr][1].find(">") != -1:
                    index = query[itr][1].find(">")
                    toProcess = query[itr][1][:index]
                    remaining = query[itr][1][index+1:]
                    operator = ">"
                elif query[itr][1].find("=") != -1:
                    index = query[itr][1].find("=")
                    toProcess = query[itr][1][:index]
                    remaining = query[itr][1][index+1:]
                    operator = "="
                else:
                    config.errorPrint("Operator not recognised in HAVING clause")
                
                attr,rel,aoper = self.getAttrRelAoper(toProcess)
                isJoin = 0
                if remaining.isnumeric():
                    value = int(remaining)
                elif remaining.find('\'') != -1:
                    value = remaining[1:-1]
                else:
                    isJoin = 1
                    self.HAVE_JOIN = 1
                if isJoin == 0:
                    self.select_conditions[-1]['relation'].append(rel)
                    self.select_conditions[-1]['attribute'].append(attr)
                    self.select_conditions[-1]['operator'].append(operator)
                    self.select_conditions[-1]['value'].append(value)
                else:
                    attr2,rel2,aoper2 = self.getAttrRelAoper(remaining)
                    self.join_conditions['relation1'].append(rel)
                    self.join_conditions['relation2'].append(rel2)
                    self.join_conditions['attribute1'].append(attr)
                    self.join_conditions['attribute2'].append(attr2)
                    self.join_conditions['operator'].append(operator)

                itr += 1

        if self.HAVE_AGGREGATES is None:
            self.HAVE_AGGREGATES = 0
        if self.HAVE_JOIN is None:
            self.HAVE_JOIN = 0

        config.debugPrint(self.relations)
        config.debugPrint(self.join_conditions)
        config.debugPrint(self.all_projects)
        config.debugPrint(self.aggregates)
        config.debugPrint(self.group_by)
        config.debugPrint(self.select_conditions)
        config.debugPrint(self.having_select)
        config.debugPrint(self.project)
        config.debugPrint("META VARIABLES")
        config.debugPrint(self.PROJECT_ALL_ATTRIBUTES)
        config.debugPrint(self.HAVING_CLAUSE_EXIST)
        config.debugPrint(self.HAVE_AGGREGATES)
        config.debugPrint(self.GROUP_BY_CLAUSE_EXIST)
        config.debugPrint(self.PART_ONE_PROJECT_ALL)
        config.debugPrint(self.SELECT_ALL)
        config.debugPrint(self.HAVE_JOIN)

    def generateTree(self):
        '''
        Function responsible for generating the initial query tree(not optimized)
        '''
        config.logger.log("Query::generateTree")
        finalNode = None
        #Generating Leaves
        self.relationNodeMap = {}
        for relation in self.relations:
            #get columns of the relation from config
            #the map in config will be generated from other python code which is not yet written
            #the map will be generated by reading the csv, or catalog from mysql
            columns = copy.deepcopy(config.relationColumnMap[relation])   ##UNCOMMENT 
            # columns = []
            currentNode = RelationNode(relation)
            currentNode.generate_attributes_list(columns)
            finalNode = currentNode
            self.relationNodeMap[relation] = currentNode
        
        #Generating Joins
        nodeConsider = copy.deepcopy(self.relationNodeMap)
        if self.HAVE_JOIN:
            finalNode = None
            for i in range(len(self.join_conditions['relation1'])):
                currentNode = JoinNode(self.join_conditions['relation1'][i],self.join_conditions['attribute1'][i],self.join_conditions['operator'][i],self.join_conditions['relation2'][i],self.join_conditions['attribute2'][i])
                
                nde = nodeConsider[currentNode.r1]
                while nde.parent is not None:
                    nde = nde.parent
                currentNode.children.append(nde)
                nde.parent = currentNode

                nde = nodeConsider[currentNode.r2]
                while nde.parent is not None:
                    nde = nde.parent
                currentNode.children.append(nde)
                nde.parent = currentNode

                currentNode.generate_attributes_list()

            #Validation Check
            defect = 0
            for i in nodeConsider:
                if finalNode is None:
                    nde = nodeConsider[i]
                    while nde.parent is not None:
                        nde = nde.parent
                    finalNode = nde
                else:
                    nde = nodeConsider[i]
                    while nde.parent is not None:
                        nde = nde.parent
                    if nde != finalNode:
                        defect = 1
                        break
            if defect:
                config.errorPrint("Error in joins, joins do not converge to one in the end")
            else:
                config.debugPrint("Joins Converge to a point, and it is correct")
            
        #select node
        if self.SELECT_ALL == 0:
            currentNode = SelectNode(self.select_conditions)
            currentNode.children.append(finalNode)
            currentNode.generate_attributes_list()
            finalNode.parent = currentNode
            finalNode = currentNode 

        #Project Node
        if self.PART_ONE_PROJECT_ALL == 0:
            currentNode = ProjectNode({'attribute' : self.all_projects['attribute'],'relation' : self.all_projects['relation']})
            currentNode.children.append(finalNode)
            currentNode.generate_attributes_list()
            finalNode.parent = currentNode
            finalNode = currentNode

        #Aggregate Node
        if self.HAVE_AGGREGATES == 1:
            currentNode = AggregateNode(self.group_by,self.aggregates,self.GROUP_BY_CLAUSE_EXIST)
            currentNode.children.append(finalNode)
            currentNode.generate_attributes_list()
            finalNode.parent = currentNode
            finalNode = currentNode
        
        #Having Node aka having Select node
        if self.HAVING_CLAUSE_EXIST == 1:
            currentNode = HavingNode(self.having_select)
            currentNode.children.append(finalNode)
            currentNode.generate_attributes_list()
            finalNode.parent = currentNode
            finalNode = currentNode

        #final project aka project node
        if self.PROJECT_ALL_ATTRIBUTES == 0:
            currentNode = ProjectNode(self.project)
            currentNode.children.append(finalNode)
            currentNode.generate_attributes_list()
            finalNode.parent = currentNode
            finalNode = currentNode

        self.ROOT_TREE_NOT_LOCALIZATION = finalNode
        config.debugPrint(type(self.ROOT_TREE_NOT_LOCALIZATION))

    def PrintTree(self,PATH):
        '''
        Function to print the query tree created.
        '''

        config.logger.log("Query::PrintTree")

        fl = open(PATH,'w')
        fl.write('```mermaid\n')
        fl.write('graph TD\n')
        fl.write('subgraph TREE\n')

        ctr = 1
        root = self.ROOT_TREE_NOT_LOCALIZATION
        mp_node_identifier = {}
        mp_identifier_node = {}
        q = []
        mp_node_identifier[root] = ctr
        mp_identifier_node[ctr] = root
        ctr += 1
        q.append(root)
        while(len(q)!=0):
            nde = q.pop(0)
            cnode = mp_node_identifier[nde]
            fl.write(str(cnode)+'['+str(cnode)+"<br/>")
            tpe = str(type(nde))
            tpe = tpe.split()[1]
            tpe = tpe[1:-2]
            fl.write("type = "+tpe+'<br/>]\n')
            if nde.parent is not None:
                ide = mp_node_identifier[nde.parent]
                fl.write(str(ide)+"-->"+str(cnode)+'\n')
            for x in nde.children:
                mp_node_identifier[x] = ctr
                mp_node_identifier[ctr] = x
                ctr += 1
                q.append(x)
        fl.write('end\n')
        fl.write('```')
        fl.close()