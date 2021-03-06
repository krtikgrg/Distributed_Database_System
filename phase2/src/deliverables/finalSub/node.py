import config
import copy
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

    def setUseOnlyAttributes(self):
        '''
        Function to setUseOnlyAttributes as 1
        '''
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
        super().__init__()

    def generate_attributes_list(self,attribs):
        '''
        Function to generate the list of attributes that will appear in this Leaf Node
        Care while passing attribs, it should be a dictionary
        '''
        config.logger.log("HFNode::generate_attributes_list")
        self.attributes = attribs
        self.remove_duplicates()

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


class RelationNode(Node):
    '''
    Class for the relation node aka leaf node that will be used in tree generation
    '''
    def __init__(self,name):
        config.logger.log("RelationNode::Constructor")

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