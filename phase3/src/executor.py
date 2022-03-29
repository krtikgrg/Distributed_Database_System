import config
from optimization import Optimizer
from node import Node, ProjectNode, SelectNode, HavingNode, AggregateNode, JoinNode, UnionNode, HFNode, VFNode, RelationNode
class Executor:
    '''
    Class for executing a given query tree
    '''
    def __init__(self,optimizer):
        config.logger.log("Executor::Constructor")
        self.optimizer = optimizer

    def dfs(self,node):
        '''
        Function which will be called recursively to traverse the tree in depth first search manner 
        '''
        config.logger.log("Executor::dfs")

        return_values = []
        for i in range(len(node.children)):
            relname,site = self.dfs(node.children[i])
            tempList = []
            tempList.append(relname)
            tempList.append(site)
            return_values.append(tempList)

        if len(return_values) == 0: #Base Case
            return node.execute()
            
        return 1,1

    def execute(self,root):
        '''
        Function which will actually execute a query
        '''
        config.logger.log("Executor::execute")
        
        self.dfs(root)

