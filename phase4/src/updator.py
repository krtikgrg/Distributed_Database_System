import config
import pandas as pd
import copy
import os

from trace import Logger
from utility import copyToServer,copyFromServer,dumpTable,importTable
class Updator:
    '''
    Class for updating a relation according to the given update command
    We use 2 Phase Commit Protocol 
    '''
    def __init__(self):
        config.logger.log("Updator::Constructor")

    def finalize(self):
        '''
        Function to do cleanup for update transaction
        '''
        config.logger.log("Updator::finalize")

        for i in config.available_sites:
            command = "rm ./Outlaws/participant_"+str(i)+".txt"
            (a,b,c) = config.paramikoConnections[i].exec_command(command)
            op = c.read()
            copyToServer(i,"participant_"+str(i)+".txt")
            # os.remove("participants_"+str(i)+".txt") ## UNCOMMENT
        
        # transfer of wrong tuples
        for i in range(len(config.Horizontal_Fragments['Fragment_Name'])):
            if config.Horizontal_Fragments['Table_Name'][i] == config.parsedQuery.updateRelation:
                curFrag = config.Horizontal_Fragments['Fragment_Name'][i]
                curSite = config.Allocation['Site'][config.Allocation['Fragment_Name'].index(curFrag)]

                for j in range(len(config.Horizontal_Fragments['Fragment_Name'])):
                    if j!=i and config.Horizontal_Fragments['Table_Name'][j] == config.parsedQuery.updateRelation:
                        altFrag = config.Horizontal_Fragments['Fragment_Name'][j]
                        altSite = config.Allocation['Site'][config.Allocation['Fragment_Name'].index(altFrag)]

                        altCondition = config.Horizontal_Fragments['Attribute'][j]+config.Horizontal_Fragments['Operator'][j]+config.Horizontal_Fragments['Val'][j]
                        print(altCondition)

                        nuTabName = altFrag+curFrag 
                        sqlQuery = "create table "+config.catalogName+"."+nuTabName+" select * from "+config.catalogName+"."+curFrag+" where "+altCondition+";"
                        print(sqlQuery)
                        # cur = config.globalConnections[curSite].cursor()
                        # cur.execute(sqlQuery)
                        # config.globalConnections[curSite].commit()

                        sqlQuery = "DELETE FROM "+config.catalogName+"."+curFrag+" WHERE "+altCondition+";"
                        print(sqlQuery)
                        # cur = config.globalConnections[curSite].cursor()
                        # cur.execute(sqlQuery)
                        # config.globalConnections[curSite].commit()

                        dumpTable(nuTabName,curSite)
                        copyFromServer(curSite)
                        copyToServer(altSite)
                        importTable(altSite)

                        finalTabName = nuTabName+"final"
                        sqlQuery = "Create Table "+config.catalogName+"."+finalTabName+" select * from "+config.catalogName+"."+altFrag+" UNION select * from "+config.catalogName+"."+nuTabName+";"
                        print(sqlQuery)
                        # cur = config.globalConnections[altSite].cursor()
                        # cur.execute(sqlQuery)
                        # config.globalConnections[altSite].commit()

                        sqlQuery = "drop table "+config.catalogName+"."altFrag+";"
                        print(sqlQuery)
                        # cur = config.globalConnections[altSite].cursor()
                        # cur.execute(sqlQuery)
                        # config.globalConnections[altSite].commit()

                        sqlQuery = "alter table "+config.catalogName+"."+finalTabName+" RENAME "+config.catalogName+"."+altFrag+";"
                        print(sqlQuery)
                        # cur = config.globalConnections[altSite].cursor()
                        # cur.execute(sqlQuery)
                        # config.globalConnections[altSite].commit()

                        # remove nuTabName at curSite, altSite
                        sqlQuery = "drop table "+config.catalogName+"."+nuTabName+";"
                        print(sqlQuery)
                        # cur = config.globalConnections[altSite].cursor()
                        # cur.execute(sqlQuery)
                        # config.globalConnections[altSite].commit()
                        sqlQuery = "drop table "+config.catalogName+"."+nuTabName+";"
                        print(sqlQuery)
                        # cur = config.globalConnections[curSite].cursor()
                        # cur.execute(sqlQuery)
                        # config.globalConnections[curSite].commit()

        return

    def generateAttributes(self):
        '''
        Function to generate the attribute list to be placed in the select clause
        '''
        config.logger.log("updator::generateAttributes")

        clause = ""
        for i in range(len(config.parsedQuery.updateAttributes['attribute'])):
            clause += config.parsedQuery.updateAttributes['attribute'][i]
            clause += " , "
        for i in range(len(config.parsedQuery.updateSelectConditions)):
            for j in range(len(config.parsedQuery.updateSelectConditions[i]['attribute'])):
                clause += config.parsedQuery.updateSelectConditions[i]['attribute'][j]    
                clause += " , "
        clause = clause[:-3]
        return clause

    def checkSite(self,site,sites_to_frags):
        '''
        Function to recieve the Vote-abort or Vote-commit message from the desired site
        '''
        config.logger.log("updator::checkSite")

        sqlQuery = "select "+self.generateAttributes()+" from "+config.catalogName+"."+sites_to_frags[site][0]+";"
        config.debugPrint(sqlQuery)
        try:
            pd.read_sql_query(sqlQuery,config.globalConnections[site])
            # testing = 1
        except:
            return 1
        else:
            return 0

    def generateSetClause(self):
        '''
        Function to generate the SET clause for the update command for a site and a fragment
        '''
        config.logger.log("updator::generateSetClause")

        clause = ""
        for i in range(len(config.parsedQuery.updateAttributes['attribute'])):
            clause += (config.parsedQuery.updateAttributes['attribute'][i]+"="+str(config.parsedQuery.updateAttributes['value'][i]))
            clause += " , "
        clause = clause[:-3]
        return clause

    def generateWhereClause(self):
        '''
        Function to generate the WHERE clause for the update command for a site and a fragment
        '''
        config.logger.log("updator::generateWhereClause")

        clause = ""
        for i in range(len(config.parsedQuery.updateSelectConditions)):
            current = "("
            for j in range(len(config.parsedQuery.updateSelectConditions[i]['attribute'])):
                current = current + config.parsedQuery.updateSelectConditions[i]['attribute'][j] + config.parsedQuery.updateSelectConditions[i]['operator'][j] + str(config.parsedQuery.updateSelectConditions[i]['value'][j]) + " OR "
            current = current[:-4]
            current += ")"
            clause += current
            clause += " AND "
        clause = clause[:-5]
        return clause

    def handleGlobalCommit(self,site,sites_to_frags):
        '''
        Function to actually commit an update operation to the targetted site
        '''
        config.logger.log("updator::handleGlobalCommit")

        frag_copy_mapper = {}
        for frag in sites_to_frags[site]:
            frag_copy_mapper[frag] = frag+"_copyy"
            sqlQuery = "CREATE TABLE "+config.catalogName+"."+frag_copy_mapper[frag]+" SELECT * FROM "+config.catalogName+"."+frag+";"
            
            cur = config.globalConnections[site].cursor()
            cur.execute(sqlQuery)
            config.globalConnections[site].commit()

            # config.tempTables[frag_copy_mapper[frag]] = [site]

        executed = 1
        for frag in sites_to_frags[site]:
            # sqlQuery = "UPDATE "+config.catalogName+"."+frag+" SET "+self.generateSetClause()+" WHERE "+self.generateWhereClause()+";"
            cpyQuery = copy.deepcopy(config.parsedQuery.updateQueryInput)
            cpyQuery[0][1] = config.catalogName+"."+frag_copy_mapper[frag]
            sqlQuery = ""
            for x in cpyQuery:
                for y in x:
                    sqlQuery += y
                    sqlQuery += " "
            sqlQuery = sqlQuery[:-1]
            sqlQuery += ";"

            # print(sqlQuery)
            # exit(0)

            try:
                cur = config.globalConnections[site].cursor()
                cur.execute(sqlQuery)
                config.globalConnections[site].commit()
            except:
                executed = 0
                break
        
        if executed == 0:
            # reverting changes in case of failures
            for frag in frag_copy_mapper:
                sqlQuery = "drop table "+config.catalogName+"."+frag_copy_mapper[frag]+";"
                cur = config.globalConnections[site].cursor()
                cur.execute(sqlQuery)
                config.globalConnections[site].commit()
        else:
            # ALTER TABLE old_table_name RENAME new_table_name
            for frag in frag_copy_mapper:
                sqlQuery = "drop table "+config.catalogName+"."+frag+";"
                cur = config.globalConnections[site].cursor()
                cur.execute(sqlQuery)
                config.globalConnections[site].commit()

                sqlQuery = "alter table "+config.catalogName+"."+frag_copy_mapper[frag]+" RENAME "+config.catalogName+"."+frag+";"
                cur = config.globalConnections[site].cursor()
                cur.execute(sqlQuery)
                config.globalConnections[site].commit()

        return executed

    def update(self):
        '''
        Function to actually execute the update by making use of 2PC protocol
        '''
        config.logger.log("Updator::update")

        sites_involved = []
        sites_to_frags = {}
        frags = []
        for i in range(len(config.Horizontal_Fragments['Table_Name'])):
            if config.Horizontal_Fragments['Table_Name'][i] == config.parsedQuery.updateRelation:
                frags.append(config.Horizontal_Fragments['Fragment_Name'][i])
        
        for i in range(len(config.Allocation['Site'])):
            if config.Allocation['Fragment_Name'][i] in frags:
                if config.Allocation['Site'][i] not in sites_to_frags:
                    sites_to_frags[config.Allocation['Site'][i]] = []
                    sites_involved.append(config.Allocation['Site'][i])
                sites_to_frags[config.Allocation['Site'][i]].append(config.Allocation['Fragment_Name'][i]) 
        
        # print(sites_to_frags)

        config.coordinator.log("begin_commit")
        message_site = {}
        for site in sites_involved:
            abort = 0
            abort = self.checkSite(site,sites_to_frags)
            if abort:
                config.participants[site].log("abort")
                message_site[site] = "Vote-abort"
            else:
                config.participants[site].log("ready")
                message_site[site] = "Vote-commit"

        unilateral_abort = 0
        for site in message_site:
            if len(message_site[site]) == 10: #got VOTE ABORT
                unilateral_abort = 1
                break
        
        if unilateral_abort:
            config.coordinator.log("abort")
            
            message = "Global-abort"
            for site in message_site:
                config.debugPrint(message)
                if len(message_site[site]) != 10:
                    # Recieving global abort
                    config.participants[site].log("abort")
                    config.participants[site].log("end_of_transaction")
                    config.participants[site].log("")

            config.coordinator.log("end_of_transaction")
            config.coordinator.log("")
        else:
            config.coordinator.log("commit")
            message = "Global-commit"

            for site in message_site:
                ack = 0
                config.participants[site].log("commit")

                while ack!=1:
                    ack = self.handleGlobalCommit(site,sites_to_frags)

                config.participants[site].log("end_of_transaction")
                config.participants[site].log("")

            config.coordinator.log("end_of_transaction")
            config.coordinator.log("")
        
        self.finalize()
        return unilateral_abort
