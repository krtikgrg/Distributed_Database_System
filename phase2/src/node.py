import config
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

    def get_attributes(self):
        '''
        Function to get the attributes of a Node
        '''

        config.logger.log("Node::get_attributes")

        return self.attributes

class ProjectNode(Node):
    '''
    Class for the project node that will be used in tree generation
    '''
    def __init__(self,to_be_projected):
        config.logger.log("ProjectNode::Constructor")
        self.to_be_projected = to_be_projected
        #dictionary
        #{
        #   'attribute':[],
        #   'relation':[]
        #}
        super().__init__()

    def generate_attributes_list(self):
        '''
        Function to generate the list of atttributes that will appear on this node 
        '''

        config.logger.log("ProjectNode::generate_attributes_list")

        self.attributes = self.to_be_projected

class SelectNode(Node):
    '''
    Class for the select node that will be used in tree generation
    '''
    def __init__(self,conditions):
        config.logger.log("SelectNode::Constructor")

        self.conditions = conditions 
        #conditions is a dictionary of the type
        #{
        #   'relation':[],
        #   'attribute':[],
        #   'operator':[],
        #   'value':[] 
        #}
        super().__init__()

    def generate_attributes_list(self):
        '''
        Function to generate the list of atttributes that will appear on this node 
        '''

        config.logger.log("SelectNode::generate_attributes_list")

        self.attributes = self.children[0].get_attributes()

class AggregateNode(Node):
    '''
    Class for the aggregate node that will be used in tree generation
    '''
    def __init__(self,group_by_attributes,aggregates):
        config.logger.log("AggregateNode::Constructor")

        self.group_by_attributes = group_by_attributes
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