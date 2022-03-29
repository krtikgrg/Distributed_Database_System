import config
from itertools import permutations
class Optimizer:
    '''
    Class for different kinds of optimizations that are to be incorporated in the code
    '''
    def __init__(self):
        config.logger.log("Optimizer::Constructor")

    def calcCost(self,joinOrder,relations):
        '''
        Given a join order, join selectivities and relation sizes
        this function is supposed to calculate the cost of their joining
        '''
        cost = 0
        relation_sz = {}
        for x in relations:
            relation_sz[x] = config.relationNumEntries[x]
        
        for x in joinOrder:
            r1 = x[0]
            r2 = x[0]

            joinSel = config.joinSelectivities[(r1,r2)]
            sz1 = relation_sz[r1]
            sz2 = relation_sz[r2]
            nusz = sz1*sz2

            cost = cost + nusz
            relation_sz[r1] = nusz*joinSel
            relation_sz[r2] = nusz*joinSel
        return cost

    def bestJoinOrder(self,join_conditions):
        '''
        Function to try all possible orderings of the given relations
        in joins. We will calculate cost for each one of the ordering
        and the one with lowest cost will be picked
        '''
        joins_involved = []
        rels_involved = set([])
        uniqs = set([])
        for i in range(len(join_conditions['relation1'])):
            if ((join_conditions['relation1'][i],join_conditions['relation2'][i]) not in uniqs) and ((join_conditions['relation2'][i], join_conditions['relation1'][i]) not in uniqs): 
                joins_involved.append([join_conditions['relation1'][i],join_conditions['relation2'][i]])
                uniqs.add((join_conditions['relation1'][i],join_conditions['relation2'][i]))
                
                rels_involved.add(join_conditions['relation2'][i])
                rels_involved.add(join_conditions['relation1'][i])

        
        # rels_involved = list(set(rels_involved))
        if len(rels_involved)>9:
            config.errorPrint("Sorry, this version does not support more than 8 joins/9 relations in a single query")
        
        config.debugPrint("less than equal to 8 joins (which is less than equal to 9 relations) present")

        perms = list(permutations(joins_involved))
        
        miniCost = None
        miniInd = None

        config.logger.log("Optimizer::CalcCost")
        for i in range(len(perms)):
            currentPermutation = perms[i]

            curCost = self.calcCost(currentPermutation,rels_involved)
            if miniCost is None:
                miniCost = curCost+1
            
            if curCost<miniCost:
                miniCost = curCost
                miniInd = i
        
        nu_join_conditions = {
            "relation1":[],
            "attribute1":[],
            "operator":[],
            "relation2":[],
            "attribute2":[]
        }

        for x in perms[miniInd]:
            for i in range(len(join_conditions['relation1'])):
                if join_conditions['relation1'][i] == x[0] and join_conditions['relation2'][i] == x[1]:
                    nu_join_conditions['relation1'].append(join_conditions['relation1'][i])
                    nu_join_conditions['attribute1'].append(join_conditions['attribute1'][i])
                    nu_join_conditions['operator'].append(join_conditions['operator'][i])
                    nu_join_conditions['relation2'].append(join_conditions['relation2'][i])
                    nu_join_conditions['attribute2'].append(join_conditions['attribute2'][i])
        
        return nu_join_conditions

    def getDirectionUnion(self,site1,len1,site2,len2):
        if len1>len2:
            return 1
        return 0