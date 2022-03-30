import config
import copy
import time
import pandas as pd
import random
from optimization import Optimizer
from utility import dumpTable, importTable, copyFromServer, copyToServer

class Node:
    '''
    Class for the node that will be used in tree generation
    '''
    def __init__(self):
        config.logger.log("Node::SuperConstructor")
        self.parent = None
        self.attributes = {
            "relation":[],
            "attribute":[]
        }
        self.children = []
        self.useOnlyAttributes = 0
        self.site = None

    def get_attributes(self):
        '''
        Function to get the attributes of a Node
        '''

        config.logger.log("Node::get_attributes")

        return copy.deepcopy(self.attributes)

    def remove_duplicates(self):
        '''
        Function to remove duplicate attributes
        '''
        config.logger.log("Node::remove_duplicates")
        attrs = {
            'relation':[],
            'attribute':[]
        }

        mper = {}
        for i in range(len(self.attributes['relation'])):
            tp = tuple([self.attributes['relation'][i],self.attributes['attribute'][i]])
            if tp not in mper:
                mper[tp] = 0
                attrs['relation'].append(self.attributes['relation'][i])
                attrs['attribute'].append(self.attributes['attribute'][i])
        
        self.attributes = attrs
        self.relationAttributeTupleMap = mper

    def getSiteInformation(self):
        '''
        Function to extract the site on which a particular relation/fragment is stored
        This function is only called for HFNode, VFNode or RelationNode
        '''
        config.logger.log("Node::getSiteInformation")
        nme = self.relation #the member relation exists in child class

        if nme in config.Allocation['Fragment_Name']:
            for i in range(len(config.Allocation['Fragment_Name'])):
                if config.Allocation['Fragment_Name'][i] == nme:
                    self.site = config.Allocation['Site'][i]
                    break

    def setUseOnlyAttributes(self):
        '''
        Function to setUseOnlyAttributes as 1
        '''
        config.logger.log("Node::setUseOnlyAttributes")
        self.useOnlyAttributes = 1

class ProjectNode(Node):
    '''
    Class for the project node that will be used in tree generation
    '''
    def __init__(self,to_be_projected):
        config.logger.log("ProjectNode::Constructor")
        self.to_be_projected = to_be_projected
        #For intermediate Project
        #dictionary
        #{
        #   'attribute':[],
        #   'relation':[]
        #}
        #for Final/Topmost project in query tree
        #dictionary
        #{
        #   'attribute':[],
        #   'relation':[]
        #   'aggregate_operator':[]
        #}
        super().__init__()

    def generate_attributes_list(self):
        '''
        Function to generate the list of atttributes that will appear on this node 
        '''

        config.logger.log("ProjectNode::generate_attributes_list")

        self.attributes = self.to_be_projected
        self.remove_duplicates()

    def generateProjectClause(self):
        '''
        Function to append all the columns to be projected
        '''
        config.logger.log("ProjectNode::generateProjectClause")

        clause = ""
        for i in range(len(self.to_be_projected['attribute'])):
            clause = clause + self.to_be_projected['attribute'][i]+" , "
        clause = clause[:-3]
        return clause

    def execute(self,re_vals):
        '''
        Executing project nodes
        '''
        config.logger.log("ProjectNode::execute")

        self.relation = re_vals[0][0]
        self.site = re_vals[0][1]
        self.lenRelation = re_vals[0][2]

        nuRel = self.relation[:5]+str(time.time()).replace(".","")
        sqlQuery = "create table "+ config.catalogName + "." + nuRel + " select "+self.generateProjectClause()+" from " + config.catalogName + "." +self.relation+";"
        
        config.debugPrint("To be Executed :: "+sqlQuery)

        cur = config.globalConnections[self.site].cursor()
        cur.execute(sqlQuery)
        config.globalConnections[self.site].commit()

        config.tempTables[nuRel] = [self.site]

        # sqlQuery = "select * from "+config.catalogName+"."+nuRel+";"
        # A = pd.read_sql_query(sqlQuery,config.globalConnections[self.site])
        # print()
        # print(A)
        return nuRel,self.site,self.lenRelation

class SelectNode(Node):
    '''
    Class for the select node that will be used in tree generation
    '''
    def __init__(self,conditions):
        config.logger.log("SelectNode::Constructor")

        self.conditions = []
        for condition in conditions:
            if condition not in self.conditions:
                self.conditions.append(condition) 
        #conditions is a list of dictionaries of the type
        #[{
        #   'relation':[],
        #   'attribute':[],
        #   'operator':[],
        #   'value':[] 
        #}]
        super().__init__()

    def generate_attributes_list(self):
        '''
        Function to generate the list of atttributes that will appear on this node 
        '''

        config.logger.log("SelectNode::generate_attributes_list")

        self.attributes = self.children[0].get_attributes()
        self.remove_duplicates()

    def getConditions(self):
        '''
        Function returing the select conditions mentioned in the select node
        '''
        config.logger.log("SelectNode::getConditions")
        return self.conditions
    
    def insertCondition(self,condition):
        '''
        Function inserting a condition in the conditions of the select node
        '''
        config.logger.log("SelectNode::insertCondition")
        self.conditions.append(condition)
        return
    
    def setConditions(self,conditions):
        '''
        Fucntion to set the conditions in the select node
        '''
        config.logger.log("SelectNode::setConditions")
        self.conditions = []
        for condition in conditions:
            self.conditions.append(condition)

    def generateWhereClause(self):
        '''
        Function to add all the select conditions in the where clause
        '''
        config.logger.log("Node::generateWhereClause")

        clause = ""
        for j in range(len(self.conditions)):
            current = "("
            for i in range(len(self.conditions[j]['attribute'])):
                current = current+self.conditions[j]['attribute'][i]+self.conditions[j]['operator'][i]+str(self.conditions[j]['value'][i])+" OR "
            current = current[:-4]
            current += ")"
            clause += current
            clause += " AND "
        
        clause = clause[:-5]
        return clause

    def execute(self,re_vals):
        '''
        Function to execute the current select node on its child node
        '''
        config.logger.log("SelectNode::execute")
        self.relation = re_vals[0][0]
        self.site = re_vals[0][1]
        self.lenRelation = int(round(random.uniform(0.3,0.5),2) * re_vals[0][2])
        if self.lenRelation == 0:
            self.lenRelation = 1

        nuRel = self.relation[:5]+str(time.time()).replace(".","")
        sqlQuery = "create table "+ config.catalogName + "." + nuRel + " select * from " + config.catalogName + "." +self.relation+" where "+ self.generateWhereClause() +";"
        
        config.debugPrint("To be Executed :: "+sqlQuery)

        cur = config.globalConnections[self.site].cursor()
        cur.execute(sqlQuery)
        config.globalConnections[self.site].commit()

        config.tempTables[nuRel] = [self.site]

        # sqlQuery = "select * from "+config.catalogName+"."+nuRel+";"
        # A = pd.read_sql_query(sqlQuery,config.globalConnections[self.site])
        # print()
        # print(A)
        return nuRel,self.site,self.lenRelation

class HavingNode(Node):
    '''
    Class for the Having node that will be used in tree generation
    '''
    def __init__(self,conditions):
        config.logger.log("HavingNode::Constructor")

        self.conditions = conditions 
        #conditions is a list of dictionaries of the type
        #[{
        #   'aggregate_operator':[],
        #   'relation':[],
        #   'attribute':[],
        #   'operator':[],
        #   'value':[] 
        #}]
        super().__init__()

    def generate_attributes_list(self):
        '''
        Function to generate the list of atttributes that will appear on this node 
        '''

        config.logger.log("HavingNode::generate_attributes_list")

        self.attributes = self.children[0].get_attributes()
        self.remove_duplicates()

class AggregateNode(Node):
    '''
    Class for the aggregate node that will be used in tree generation
    '''
    def __init__(self,group_by_attributes,aggregates,group_by_exist):
        config.logger.log("AggregateNode::Constructor")

        self.group_by_exist = group_by_exist
        if self.group_by_exist:
            self.group_by_attributes = group_by_attributes
        else:
            self.group_by_attributes = {
                'attribute':[],
                'relation':[]
            }
        #dictionary
        #{
        #   'attribute':[],
        #   'relation':[]
        #}
        self.aggregates = aggregates
        #dictionary
        #{
        #   'operator':[],
        #   'attribute':[],
        #   'relation':[]    
        #}
        super().__init__()

    def generate_attributes_list(self):
        '''
        Function to generate the list of atttributes that will appear on this node 
        '''

        config.logger.log("AggregateNode::generate_attributes_list")

        self.attributes = self.children[0].get_attributes()
        attr = []
        rel = []
        for i in range(len(self.aggregates['attribute'])):
            attr.append(self.aggregates['operator'][i] + '_' + self.aggregates['relation'][i] + "_" + self.aggregates['attribute'][i])
            rel.append(self.aggregates['relation'][i])
        self.attributes['attribute'] += attr
        self.attributes['relation'] += rel
        self.remove_duplicates()

class JoinNode(Node):
    '''
    Class for the join node that will be used in tree generation
    '''
    def __init__(self,r1_name,r1_attribute,operator,r2_name,r2_attribute):
        config.logger.log("JoinNode::Constructor")

        self.r1 = r1_name
        self.r1_attribute = r1_attribute
        self.operator = operator
        self.r2 = r2_name
        self.r2_attribute = r2_attribute
        super().__init__()

    def generate_attributes_list(self):
        '''
        Function to generate the list of atttributes that will appear on this node 
        '''

        config.logger.log("JoinNode::generate_attributes_list")

        a1 = self.children[0].get_attributes()
        a2 = self.children[1].get_attributes()
        #concatenating both the lists
        for i in range(len(a2['relation'])):
            a1['relation'].append(a2['relation'][i])
            a1['attribute'].append(a2['attribute'][i])
        self.attributes = a1
        self.remove_duplicates()

    def getColumns(self,t1name):
        '''
        Function to get all the columns which are to be added in the sql query
        '''
        config.logger.log("JoinNode::getColumns")

        clause = ""
        for x in range(len(self.attributes['attribute'])):
            if self.attributes['attribute'][x] != self.r1_attribute:
                clause = clause+self.attributes['attribute'][x]
            else:
                clause = clause+t1name+"."+self.attributes['attribute'][x]
            clause=clause+" , "
        clause = clause[:-3]
        return clause

    def getChildColumns(self,index,tname,jattr):
        '''
        Fucntion to get columns of the child on index 
        '''
        config.logger.log("JoinNode::getChildColumns")

        clause = ""
        attrs = self.children[index].get_attributes()
        for x in range(len(attrs['attribute'])):
            if attrs['attribute'][x] != jattr:
                clause = clause + attrs['attribute'][x]+" , "
            else:
                clause = clause+tname+"."+attrs['attribute'][x]+" , "
        clause = clause[:-3]
        return clause

    def execute(self,re_vals):
        '''
        Function to execute the join at this particular JoinNode
        '''
        config.logger.log("JoinNode::execute")

        table1Name = re_vals[0][0]
        table1Site = re_vals[0][1]
        table1Leng = re_vals[0][2]

        table2Name = re_vals[1][0]
        table2Site = re_vals[1][1]
        table2Leng = re_vals[1][2]

        if table1Site == table2Site:
            self.site = table1Site
            self.lenRelation = table1Leng*table2Leng*config.joinSelectivities[(self.r1,self.r2)]
            #execute join directly here
            nuRel = table1Name[:5]+table2Name[:5]+str(time.time()).replace(".","")
            # SELECT * FROM Orders INNER JOIN Customers ON Orders.CustomerID=Customers.CustomerID;
            if self.r1_attribute == self.r2_attribute:
                temp = " SELECT "+self.getColumns(table1Name) +" FROM "+config.catalogName+"."+table1Name + " INNER JOIN "+config.catalogName+"."+table2Name+" ON "+config.catalogName+"."+table1Name+"."+self.r1_attribute+"="+config.catalogName+"."+table2Name+"."+self.r2_attribute+";"
            else:
                temp = " SELECT * FROM "+config.catalogName+"."+table1Name + " INNER JOIN "+config.catalogName+"."+table2Name+" ON "+config.catalogName+"."+table1Name+"."+self.r1_attribute+"="+config.catalogName+"."+table2Name+"."+self.r2_attribute+";"
            sqlQuery = "create table "+ config.catalogName + "." + nuRel + temp
            cur = config.globalConnections[self.site].cursor()
            cur.execute(sqlQuery)
            config.globalConnections[self.site].commit()
            config.tempTables[nuRel] = [self.site]
            # sqlQuery = "select * from "+config.catalogName+"."+nuRel+";"
            # A = pd.read_sql_query(sqlQuery,config.globalConnections[self.site])
            # print()
            # print(A)
            return nuRel,self.site,self.lenRelation
        else:
            direction = config.parsedQuery.optimizer.getDirectionJoin(re_vals,self.r1,self.r1_attribute,self.r2,self.r2_attribute)
            # direction = 1
            if direction == 0:
                #move 2 to 1
                self.site = table1Site

                ojoiattr = table1Name[:5]+str(time.time()).replace(".","")
                sqlQuery = "create table "+ config.catalogName + "." + ojoiattr + " SELECT DISTINCT "+ self.r1_attribute +" FROM "+config.catalogName+"."+table1Name+";"
                # print(sqlQuery)

                cur1 = config.globalConnections[table1Site].cursor()
                cur1.execute(sqlQuery)
                config.globalConnections[table1Site].commit()
                config.tempTables[ojoiattr] = [table1Site]

                dumpTable(ojoiattr,table1Site)
                copyFromServer(table1Site)
                copyToServer(table2Site)
                importTable(table2Site)
                config.tempTables[ojoiattr].append(table2Site)

                trelrows = table2Name[:5]+str(time.time()).replace(".","")
                sqlQuery = "create table "+ config.catalogName + "." + trelrows + " SELECT "+self.getChildColumns(1,table2Name,self.r2_attribute) + " FROM "+config.catalogName+"."+table2Name+" INNER JOIN "+config.catalogName+"."+ojoiattr+" ON "+config.catalogName+"."+table2Name+"."+self.r2_attribute+"="+config.catalogName+"."+ojoiattr+"."+self.r1_attribute+";"
                # print(sqlQuery)
                cur2 = config.globalConnections[table2Site].cursor()
                cur2.execute(sqlQuery)
                config.globalConnections[table2Site].commit()
                config.tempTables[trelrows] = [table2Site]

                dumpTable(trelrows,table2Site)
                copyFromServer(table2Site)
                copyToServer(table1Site)
                importTable(table1Site)
                config.tempTables[trelrows].append(table1Site)

                nuRel = table1Name[:5]+table2Name[:5]+str(time.time()).replace(".","")

                if self.r1_attribute == self.r2_attribute:
                    temp = " SELECT "+self.getColumns(table1Name) +" FROM "+config.catalogName+"."+table1Name + " INNER JOIN "+config.catalogName+"."+trelrows+" ON "+config.catalogName+"."+table1Name+"."+self.r1_attribute+"="+config.catalogName+"."+trelrows+"."+self.r2_attribute+";"
                else:
                    temp = " SELECT * FROM "+config.catalogName+"."+table1Name + " INNER JOIN "+config.catalogName+"."+trelrows+" ON "+config.catalogName+"."+table1Name+"."+self.r1_attribute+"="+config.catalogName+"."+trelrows+"."+self.r2_attribute+";"
                
                sqlQuery = "create table "+ config.catalogName + "." + nuRel + temp
                # print(sqlQuery)
                
                cur1.execute(sqlQuery)
                config.globalConnections[table1Site].commit()
                config.tempTables[nuRel] = [table1Site]

                # sqlQuery = "select * from "+config.catalogName+"."+nuRel+";"
                # A = pd.read_sql_query(sqlQuery,config.globalConnections[self.site])
                # print()
                # print(A)

                self.lenRelation = table1Leng*table2Leng*config.joinSelectivities[(self.r1,self.r2)]

                #check other lenRelation too
                if self.lenRelation == 0:
                    self.lenRelation=1

                return nuRel,self.site,self.lenRelation   
            else:
                #move 1 to 2
                self.site = table2Site

                ojoiattr = table2Name[:5]+str(time.time()).replace(".","")
                sqlQuery = "create table "+ config.catalogName + "." + ojoiattr + " SELECT DISTINCT "+ self.r2_attribute +" FROM "+config.catalogName+"."+table2Name+";"
                # print(sqlQuery)

                cur2 = config.globalConnections[table2Site].cursor()
                cur2.execute(sqlQuery)
                config.globalConnections[table2Site].commit()
                config.tempTables[ojoiattr] = [table2Site]

                dumpTable(ojoiattr,table2Site)
                copyFromServer(table2Site)
                copyToServer(table1Site)
                importTable(table1Site)
                config.tempTables[ojoiattr].append(table1Site)

                trelrows = table1Name[:5]+str(time.time()).replace(".","")
                sqlQuery = "create table "+ config.catalogName + "." + trelrows + " SELECT "+self.getChildColumns(0,table1Name,self.r1_attribute) + " FROM "+config.catalogName+"."+table1Name+" INNER JOIN "+config.catalogName+"."+ojoiattr+" ON "+config.catalogName+"."+table1Name+"."+self.r1_attribute+"="+config.catalogName+"."+ojoiattr+"."+self.r2_attribute+";"
                # print(sqlQuery)
                cur1 = config.globalConnections[table1Site].cursor()
                cur1.execute(sqlQuery)
                config.globalConnections[table1Site].commit()
                config.tempTables[trelrows] = [table1Site]

                dumpTable(trelrows,table1Site)
                copyFromServer(table1Site)
                copyToServer(table2Site)
                importTable(table2Site)
                config.tempTables[trelrows].append(table2Site)

                nuRel = table2Name[:5]+table1Name[:5]+str(time.time()).replace(".","")

                if self.r1_attribute == self.r2_attribute:
                    temp = " SELECT "+self.getColumns(table2Name) +" FROM "+config.catalogName+"."+table2Name + " INNER JOIN "+config.catalogName+"."+trelrows+" ON "+config.catalogName+"."+table2Name+"."+self.r2_attribute+"="+config.catalogName+"."+trelrows+"."+self.r1_attribute+";"
                else:
                    temp = " SELECT * FROM "+config.catalogName+"."+table2Name + " INNER JOIN "+config.catalogName+"."+trelrows+" ON "+config.catalogName+"."+table2Name+"."+self.r2_attribute+"="+config.catalogName+"."+trelrows+"."+self.r1_attribute+";"
                
                sqlQuery = "create table "+ config.catalogName + "." + nuRel + temp
                # print(sqlQuery)
                
                cur2.execute(sqlQuery)
                config.globalConnections[table2Site].commit()
                config.tempTables[nuRel] = [table2Site]

                # sqlQuery = "select * from "+config.catalogName+"."+nuRel+";"
                # A = pd.read_sql_query(sqlQuery,config.globalConnections[self.site])
                # print()
                # print(A)

                self.lenRelation = table1Leng*table2Leng*config.joinSelectivities[(self.r2,self.r1)]

                #check other lenRelation too
                if self.lenRelation == 0:
                    self.lenRelation=1

                return nuRel,self.site,self.lenRelation
                #execute

class UnionNode(Node):
    '''
    Class for representing union, to be used in performing localization(horizonatal fragmentation)
    '''
    def __init__(self):
        config.logger.log("UnionNode::Constructor")
        # self.attribute = attribute
        # self.value = value
        # self.operator = operator
        super().__init__()

    def generate_attributes_list(self):
        '''
        Function to generate the list of attributes that will appear in this Union Node
        Care while passing attribs, it should be a dictionary
        '''
        config.logger.log("UnionNode::generate_attributes_list")
        self.attributes = copy.deepcopy(self.children[0].attributes)
        self.remove_duplicates()

    def execute(self,re_vals):
        '''
        Function to execute Union Node function
        '''    
        config.logger.log("UnionNode::execute")

        table1Name = re_vals[0][0]
        table1Site = re_vals[0][1]
        table1Leng = re_vals[0][2]

        table2Name = re_vals[1][0]
        table2Site = re_vals[1][1]
        table2Leng = re_vals[1][2]

        self.lenRelation = table1Leng+table2Leng

        if table1Site == table2Site: #Same Site Union
            #no Copying
            # execute query
            self.site = table1Site
            #return 
        else: #different site Union
            direction = config.parsedQuery.optimizer.getDirectionUnion(table1Site,table1Leng,table2Site,table2Leng)
            if direction == 0:
                #copying from site2 to site1
                dumpTable(table2Name,table2Site)
                copyFromServer(table2Site)
                copyToServer(table1Site)
                importTable(table1Site)
                #add to tempTables
                config.tempTables[table2Name].append(table1Site)
                #execute query
                self.site = table1Site
                # return
            else:
                #copying from site1 to site2
                dumpTable(table1Name,table1Site)
                copyFromServer(table1Site)
                copyToServer(table2Site)
                importTable(table2Site)
                #add to tempTables
                config.tempTables[table1Name].append(table2Site)
                #execute query
                self.site = table2Site
                # return
        
        nuRel = table1Name[:5]+table2Name[:5]+str(time.time()).replace(".","")
        sqlQuery = "create table "+ config.catalogName + "." + nuRel + " select * from " + config.catalogName + "." +table1Name+" UNION select * from " + config.catalogName + "." +table2Name+";"
    
        cur = config.globalConnections[self.site].cursor()
        cur.execute(sqlQuery)
        config.globalConnections[self.site].commit()
        config.tempTables[nuRel] = [self.site]

        # sqlQuery = "select * from "+config.catalogName+"."+nuRel+";"
        # A = pd.read_sql_query(sqlQuery,config.globalConnections[self.site])
        # print()
        # print(A)

        return nuRel,self.site,self.lenRelation

class HFNode(Node):
    '''
    Class for representing fragments which will be incorporated while localization
    After localization the fragments which will be included are not represented using the 
    RelationNode class but using this LeafNode
    Used For HFs only
    '''

    def __init__(self,namerel,attribute,operator,value,namepar):
        config.logger.log("HFNode::Constructor")

        self.relation = namerel
        self.attr = attribute
        self.value = value
        self.operator = operator
        self.parentFragmentation = namepar
        self.lenRelation = config.relationNumEntries[namerel]
        super().__init__()

    def generate_attributes_list(self,attribs):
        '''
        Function to generate the list of attributes that will appear in this Leaf Node
        Care while passing attribs, it should be a dictionary
        '''
        config.logger.log("HFNode::generate_attributes_list")
        self.attributes = attribs
        self.remove_duplicates()

        self.getSiteInformation()

    def execute(self):
        '''
        Function to execute this particular Node
        '''
        config.logger.log("HFNode::execute")

        nuRel = self.relation+str(time.time()).replace(".","")
        sqlQuery = "create table "+ config.catalogName + "." + nuRel + " select * from " + config.catalogName + "." +self.relation+";"
        
        cur = config.globalConnections[self.site].cursor()
        cur.execute(sqlQuery)
        config.globalConnections[self.site].commit()

        config.tempTables[nuRel] = [self.site]

        # return nuRel,self.site

        # sqlQuery = "select * from "+config.catalogName+"."+nuRel+";"
        # A = pd.read_sql_query(sqlQuery,config.globalConnections[self.site])
        # print()
        # print(A)
        
        # nuqry = "create temporary table if not exists "+ config.catalogName+ ".tempo;"
        # cur = config.globalConnections[self.site+1].cursor()
        # cur.execute(nuqry)
        # # config.globalConnections[self.site+1].commit()

        # A.to_sql(name='tempo',con=config.globalConnections[self.site+1],schema=config.catalogName,flavor= 'mysql',index=False)
        return nuRel,self.site,self.lenRelation

class VFNode(Node):
    '''
    Class for representing fragments which will be incorporated while localization
    After localization the fragments which will be included are not represented using the 
    RelationNode class but using this LeafNode
    Used For HFs only
    '''
    def __init__(self,namerel,parname):
        config.logger.log("VFNode::Constructor")
        self.relation = namerel
        self.parentFragmentation = parname
        self.lenRelation = config.relationNumEntries[namerel]
        super().__init__()

    def generate_attributes_list(self,attribs):
        '''
        Function to generate the list of attributes that will appear on this node 
        '''
        
        config.logger.log("VFNode::generate_attributes_list")

        rel = []
        for i in range(len(attribs)):
            rel.append(self.parentFragmentation)
        dic = {
            'attribute':attribs,
            'relation':rel
        }
        self.attributes = dic
        self.remove_duplicates()
        self.getSiteInformation()

    def execute(self):
        '''
        Function to execute this particular Node
        '''
        config.logger.log("VFNode::execute")

        nuRel = self.relation+str(time.time()).replace(".","")
        sqlQuery = "create table "+ config.catalogName + "." + nuRel + " select * from " + config.catalogName + "." +self.relation+";"
        
        cur = config.globalConnections[self.site].cursor()
        cur.execute(sqlQuery)
        config.globalConnections[self.site].commit()

        config.tempTables[nuRel] = [self.site]
        return nuRel,self.site,self.lenRelation

class RelationNode(Node):
    '''
    Class for the relation node aka leaf node that will be used in tree generation
    '''
    def __init__(self,name):
        config.logger.log("RelationNode::Constructor")

        self.lenRelation = config.relationNumEntries[name]
        self.relation = name
        super().__init__()

    def generate_attributes_list(self,attribs):
        '''
        Function to generate the list of attributes that will appear on this node 
        '''
        
        config.logger.log("RelationNode::generate_attributes_list")

        rel = []
        for i in range(len(attribs)):
            rel.append(self.relation)
        dic = {
            'attribute':attribs,
            'relation':rel
        }
        self.attributes = dic
        self.remove_duplicates()
        self.getSiteInformation()

    def execute(self):
        '''
        Function to execute this particular Node
        '''
        config.logger.log("RelationNode::execute")

        nuRel = self.relation+str(time.time()).replace(".","")
        sqlQuery = "create table "+ config.catalogName + "." + nuRel + " select * from " + config.catalogName + "." +self.relation+";"
        
        cur = config.globalConnections[self.site].cursor()
        cur.execute(sqlQuery)
        config.globalConnections[self.site].commit()

        config.tempTables[nuRel] = [self.site]
        return nuRel,self.site,self.lenRelation