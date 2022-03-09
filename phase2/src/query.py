import config
import sqlparse
import copy
from sql_metadata import Parser
from node import Node,ProjectNode,SelectNode,AggregateNode,JoinNode,UnionNode,RelationNode,HavingNode,HFNode,VFNode
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
                config.errorPrint("No relation contained the specified column "+col)
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
                    config.errorPrint("Operator not recognised in WHERE clause")
                
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
            
            if len(self.select_conditions[-1]['relation'])==0:
                self.SELECT_ALL = 1


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
        if self.PROJECT_ALL_ATTRIBUTES == 0 and (self.HAVING_CLAUSE_EXIST == 1 or self.HAVE_AGGREGATES == 1):
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
            if nde.parent is not None:
                fl.write("type = "+tpe+'<br/>'+"Parent = "+str(mp_node_identifier[nde.parent])+'<br/>')
            else:
                fl.write("type = "+tpe+'<br/>'+'Root Node'+'<br/>')
            fl.write('<br/>')
            for x in nde.attributes:
                fl.write(str(x)+" = ")
                for temp in nde.attributes[x]:
                    fl.write(str(temp)+" ")
                fl.write('<br/>')
            fl.write('<br/>')
            if tpe == "node.SelectNode":
                for i in range(len(nde.conditions)):
                    fl.write('Condition '+ str(i) +' = '+'<br/>')
                    for x in nde.conditions[i]:
                        fl.write(str(x)+" = ")
                        for temp in nde.conditions[i][x]:
                            fl.write(str(temp)+" ")
                        fl.write('<br/>')
            fl.write('<br/>')
            if tpe == "node.HFNode":
                fl.write("Horizontally Fragmented Condition = <br/>")
                fl.write("Attribute = "+str(nde.attr)+"<br/>")
                fl.write("Operator = "+str(nde.operator)+"<br/>")
                fl.write("Value = "+str(nde.value)+"<br/>")
            fl.write('<br/>')
            fl.write(']\n')

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

    def generateMapRelationAttribute(self,rels,attrs):
        '''
        Function to generate unique relation,attribute pairs
        out of all the conditions mentioned in ORs for a 
        particular conditon coming in ANDs in where clause
        '''
        config.logger.log("Query::generateMapRelationAttribute")
        mper = {}
        for i in range(len(rels)):
            tp = tuple([rels[i],attrs[i]])
            if tp not in mper:
                mper[tp] = 0
        return mper

    def insertNodeSelectTree(self,condition,curNode,index):
        '''
        Function inserting node in between two nodes
        '''

        config.logger.log('Query::insertNodeSelectTree')

        if len(curNode.parent.children) == 1:
            if condition in curNode.parent.conditions:
                return 0
            else:
                curNode.parent.insertCondition(condition)
                return 1

        nuNode = SelectNode([copy.deepcopy(condition)])
        nuNode.children.append(curNode)
        nuNode.generate_attributes_list()
        nuNode.parent = curNode.parent
        curNode.parent = nuNode
        nuNode.parent.children[index] = nuNode
        return 1

    def pushDownSelect(self,curNode,mps,condition,index):
        '''
        Actual Function responsible for pushing down the selection
        '''
        config.logger.log("Query::pushDownSelect")

        if len(curNode.children) == 0:
            #encountering a relation node
            #condition,curNode,index
            return self.insertNodeSelectTree(condition,curNode,index)
        elif len(curNode.children) == 2:
            #encountering a join node
            lmper = curNode.children[0].relationAttributeTupleMap
            rmper = curNode.children[1].relationAttributeTupleMap

            #checking for left child
            ansNode = 0
            foundAll = 1
            for x in mps:
                if x not in lmper:
                    foundAll = 0
                    break
            if foundAll == 0:
                ansNode += 1
                foundAll = 1
                for x in mps:
                    if x not in rmper:
                        foundAll = 0
                        break
                if foundAll == 0:
                    return self.insertNodeSelectTree(condition,curNode,index)
            
            return self.pushDownSelect(curNode.children[ansNode],mps,condition,ansNode)
        else:
            #encountering a previously moved down select node
            return self.pushDownSelect(curNode.children[0],mps,condition,0)

    def optimizeTreeSelection(self):
        '''
        Function to push down selection as descibed in the readme file
        Acts as a wrapper over the actual function
        '''
        config.logger.log("Query::optimizeTreeSelection")

        if self.SELECT_ALL == 1:
            config.debugPrint("We have to select all so no optimization in selections")
            return
        config.debugPrint("Trying to push down selections in the query tree")
        nde = self.ROOT_TREE_NOT_LOCALIZATION
        while True:
            tpe = str(type(nde))
            tpe = tpe.split()[1]
            tpe = tpe[1:-2]
            if tpe == 'node.SelectNode':
                break
            nde = nde.children[0]
        if len(nde.children[0].children) == 0:
            #encountered the relation node right below the select node
            #we cannot push selects further down here, so returning in this case
            return


        # On moving a select node down, i can only encounter
        # either a JOIN NODE, or a SELECT NODE(previously sent down), or a RELATION NODE

        nuConditions = []
        
        conditions = nde.getConditions()
        for i in range(len(conditions)):
            mps = self.generateMapRelationAttribute(conditions[i]['relation'],conditions[i]['attribute'])
            done = self.pushDownSelect(nde.children[0],mps,conditions[i],0)
            if done == 0:
                nuConditions.append(conditions[i])

        nde.setConditions(nuConditions)
        
    def insertNodeProjectTree(self,curNode,mps,index):
        '''
        Function to insert a project node that has been moved down
        '''

        config.logger.log("Query::insertNodeProjectTree")

        #CODE to insert project node, yet to be written
        tpe = str(type(curNode.parent))
        tpe = tpe.split()[1]
        tpe = tpe[1:-2]
        if tpe == 'node.ProjectNode':
            return 0

        if len(curNode.parent.children) == 1:
            #above node is a select node
            curNode = curNode.parent
            par = curNode.parent
            ind = 0
            for i in range(len(par.children)):
                if par.children[i] == curNode:
                    break
            ind = i
            return self.insertNodeProjectTree(curNode,mps,ind)
        
        to_be_projected = {
            'attribute':[],
            'relation':[]
        }
        for tp in mps:
            to_be_projected['relation'].append(tp[0])
            to_be_projected['attribute'].append(tp[1])
        
        nuNode = ProjectNode(to_be_projected)
        nuNode.children.append(curNode)
        nuNode.generate_attributes_list()
        nuNode.parent = curNode.parent
        curNode.parent = nuNode
        nuNode.parent.children[index] = nuNode
        
        nde = nuNode.parent
        while nde is not None:
            nde.generate_attributes_list()
            nde = nde.parent
        return 1


    def pushDownProject(self,curNode,mps,index):
        '''
        Actual Function responsibe for pushing down the project node
        '''

        config.logger.log("Query::pushDownProject")

        if len(curNode.children) == 0:
            #relation node
            #insert project node
            return self.insertNodeProjectTree(curNode,mps,index)
        elif len(curNode.children) == 1:
            #select node
            return self.pushDownProject(curNode.children[0],mps,0)
        else:
            #join node
            lmps = copy.deepcopy(mps)
            tp = tuple([curNode.r1,curNode.r1_attribute])
            addAboveCurrent = 0
            if tp not in lmps:
                addAboveCurrent = 1
                lmps[tp] = 0

            rmps = copy.deepcopy(mps)
            tp = tuple([curNode.r2,curNode.r2_attribute])
            if tp not in rmps:
                addAboveCurrent = 1
                rmps[tp] = 0

            lmper = curNode.children[0].relationAttributeTupleMap
            rmper = curNode.children[1].relationAttributeTupleMap

            nlmps = {}
            nrmps = {}
            left = 0
            right = 0
            for tp in lmps:
                if tp in lmper:
                    nlmps[tp] = 0
                    left = 1
            for tp in rmps:
                if tp in rmper:
                    nrmps[tp] = 0
                    right = 1
            
            eoleft = 0
            eoright = 0
            for tp in lmper:
                if tp not in nlmps:
                    eoleft = 1
                    break
            for tp in rmper:
                if tp not in nrmps:
                    eoright = 1
                    break

            if left and eoleft:
                self.pushDownProject(curNode.children[0],nlmps,0)
            if right and eoright:        
                self.pushDownProject(curNode.children[1],nrmps,1)
            if addAboveCurrent:
                return self.insertNodeProjectTree(curNode,mps,index)
            return 0
            # Dict.pop(Key)
                        

    def optimizeTreeProjection(self):
        '''
        Function to push down projections in the query tree so as to optimize the query execution
        By reducing the intermediate relation sizes
        '''
        config.logger.log("Query::optimizeTreeProjection")

        if self.PART_ONE_PROJECT_ALL == 1:
            config.debugPrint("We have to project all the columns so there cannot be any improvement")
            return
        
        config.debugPrint("Trying to push down projects")

        ctr = 0
        maxi = 2
        if not(self.PROJECT_ALL_ATTRIBUTES == 0 and (self.HAVING_CLAUSE_EXIST == 1 or self.HAVE_AGGREGATES == 1)):
            maxi -= 1

        # if self.PROJECT_ALL_ATTRIBUTES != 0:
            # maxi -= 1

        nde = self.ROOT_TREE_NOT_LOCALIZATION
        while True:
            tpe = str(type(nde))
            tpe = tpe.split()[1]
            tpe = tpe[1:-2]
            if tpe == 'node.ProjectNode':
                ctr += 1
                if ctr == maxi:
                    break
            nde = nde.children[0]
        if len(nde.children[0].children) == 0:
            #encountered the relation node right below the select node
            #we cannot push projects further down here, so returning in this case
            return

        # On moving a project node down, i can only encounter
        # either a JOIN NODE, or a SELECT NODE(previously sent down), or a RELATION NODE

        mps = self.generateMapRelationAttribute(nde.attributes['relation'],nde.attributes['attribute'])

        self.pushDownProject(nde.children[0],mps,0)
    
    def replaceRelationsWithFragments(self):
        '''
        Function to incorporate fragments in the query tree, and rewrite the query tree accordingly
        Basically Data Localization
        '''

        config.logger.log("Query::replaceRelationsWithFragments")

        q = []
        relNodes = []
        root = self.ROOT_TREE_NOT_LOCALIZATION
        q.append(root)
        while len(q)!=0:
            nde = q.pop(0)

            tpe = str(type(nde))
            tpe = tpe.split()[1]
            tpe = tpe[1:-2]

            if tpe == "node.RelationNode":
                relNodes.append(nde)
            
            for x in nde.children:
                q.append(x)
        
        for relNode in relNodes:
            name = relNode.relation
            if name in config.Tables['Name']:
                indx = config.Tables['Name'].index(name)
                ftype = config.Tables['Fragmentation_Type'][indx]
                # numFrags = config.Tables['Number_Of_Fragments'][indx]
                if ftype is not None:
                    if ftype == "HF":
                        leaveNodes = []
                        for i in range(len(config.Horizontal_Fragments['Table_Name'])):
                            if config.Horizontal_Fragments['Table_Name'][i] == name:
                                curNode = HFNode(config.Horizontal_Fragments['Fragment_Name'][i],config.Horizontal_Fragments['Attribute'][i],config.Horizontal_Fragments['Operator'][i],config.Horizontal_Fragments['Val'][i],name)
                                curNode.generate_attributes_list(relNode.get_attributes())
                                curNode.setUseOnlyAttributes()
                                leaveNodes.append(curNode)

                        child = UnionNode()
                        child.children.append(leaveNodes[0])
                        child.setUseOnlyAttributes()
                        leaveNodes[0].parent = child

                        for i in range(1,len(leaveNodes)-1):
                            child.children.append(leaveNodes[i])
                            leaveNodes[i].parent = child
                            child.generate_attributes_list()

                            nuChild = UnionNode()
                            nuChild.children.append(child)
                            nuChild.setUseOnlyAttributes()
                            child.parent = nuChild
                            child = nuChild
                        
                        child.children.append(leaveNodes[-1])
                        leaveNodes[-1].parent = child
                        child.generate_attributes_list()

                        par = relNode.parent
                        if par is not None:
                            ndIndx = 0
                            for i in range(len(par.children)):
                                if par.children[i] == relNode:
                                    ndIndx = i
                                    break
                            par.children[ndIndx] = child
                            child.parent = par
                        else:
                            self.ROOT_TREE_NOT_LOCALIZATION = child
                    elif ftype == "VF":
                        leaveNodes = []
                        for idx in range(len(config.Vertical_Fragments['Table_Name'])):
                            if config.Vertical_Fragments['Table_Name'][idx] == name:
                                fragName = config.Vertical_Fragments['Fragment_Name'][idx]
                                cols = []
                                for idx2 in range(len(config.VF_Columns['Fragment_Name'])):
                                    if config.VF_Columns["Fragment_Name"][idx2] == fragName:
                                        cols.append(config.VF_Columns['Column_Name'][idx2])
                                curNode = VFNode(fragName,name)
                                curNode.generate_attributes_list(copy.deepcopy(cols))
                                curNode.setUseOnlyAttributes()
                                leaveNodes.append(curNode)
                        
                        child = JoinNode(name,config.TableKeys[name],"=",name,config.TableKeys[name])
                        child.children.append(leaveNodes[0])
                        child.setUseOnlyAttributes()
                        leaveNodes[0].parent = child

                        for idx in range(1,len(leaveNodes)-1):
                            child.children.append(leaveNodes[i])
                            leaveNodes[i].parent = child
                            child.generate_attributes_list()

                            nuChild = JoinNode(name,config.TableKeys[name],"=",name,config.TableKeys[name])
                            nuChild.children.append(child)
                            nuChild.setUseOnlyAttributes()
                            child.parent = nuChild
                            child = nuChild

                        child.children.append(leaveNodes[-1])
                        leaveNodes[-1].parent = child
                        child.generate_attributes_list()

                        par = relNode.parent
                        if par is not None:
                            ndIndx = 0
                            for idx in range(len(par.children)):
                                if par.children[idx] == relNode:
                                    ndIndx = idx
                                    break
                            par.children[ndIndx] = child
                            child.parent = par
                        else:
                            self.ROOT_TREE_NOT_LOCALIZATION = child
                    else:
                        leaveNodes = []
                        for i in range(len(config.Derived_Horizontal_Fragments['Table_Name'])):
                            if config.Derived_Horizontal_Fragments['Table_Name'][i] == name:
                                idx = i
                                while config.Derived_Horizontal_Fragments['Direct_Fragment'][idx] != 1:
                                    depfrag = config.Derived_Horizontal_Fragments['Horizontal_Fragment_Name'][idx]
                                    idx = config.Derived_Horizontal_Fragments['Fragment_Name'].index(depfrag)
                                
                                HFRAGNAME = config.Derived_Horizontal_Fragments['Horizontal_Fragment_Name'][idx]
                                idx = config.Horizontal_Fragments['Fragment_Name'].index(HFRAGNAME)
                                
                                curNode = HFNode(config.Derived_Horizontal_Fragments['Fragment_Name'][i],config.Horizontal_Fragments['Attribute'][idx],config.Horizontal_Fragments['Operator'][idx],config.Horizontal_Fragments['Val'][idx],name)
                                curNode.generate_attributes_list(relNode.get_attributes())
                                curNode.setUseOnlyAttributes()
                                leaveNodes.append(curNode)

                        child = UnionNode()
                        child.children.append(leaveNodes[0])
                        child.setUseOnlyAttributes()
                        leaveNodes[0].parent = child

                        for i in range(1,len(leaveNodes)-1):
                            child.children.append(leaveNodes[i])
                            leaveNodes[i].parent = child
                            child.generate_attributes_list()

                            nuChild = UnionNode()
                            nuChild.children.append(child)
                            nuChild.setUseOnlyAttributes()
                            child.parent = nuChild
                            child = nuChild
                        
                        child.children.append(leaveNodes[-1])
                        leaveNodes[-1].parent = child
                        child.generate_attributes_list()

                        par = relNode.parent
                        if par is not None:
                            ndIndx = 0
                            for i in range(len(par.children)):
                                if par.children[i] == relNode:
                                    ndIndx = i
                                    break
                            par.children[ndIndx] = child
                            child.parent = par
                        else:
                            self.ROOT_TREE_NOT_LOCALIZATION = child
            else:
                config.errorPrint("Relation not found in Tables dictionary, name = "+str(name))