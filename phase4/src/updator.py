import config

from trace import Logger
from utility import copyToServer
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

        for i in range(1,5):
            copyToServer(i,"participants_"+str(i)+".txt")
        return

    def update(self):
        '''
        Function to actually execute the update by making use of 2PC protocol
        '''
        config.logger.log("Updator::update")

        coordinator = Logger("./coordinator_logs.txt")
        participants = {}
        for i in range(1,5):
            participants[i] = Logger("./participant_"+str(i)+".txt")

        sites_involved = []
        sites_to_frags = []
        frags = []
        for i in range(len(config.Horizontal_Fragments['Table_Name'])):
            if config.Horizontal_Fragments['Table_Name'][i] == config.parsedQuery.updateRelation:
                frags.append(config.Horizontal_Fragments['Fragment_Name'][i])
        
        for i in range(len(config.Allocation)):
            if config.Allocation['Fragment_Name'][i] in frags:
                if config.Allocation['Site'][i] not in sites_to_frags:
                    sites_to_frags[config.Allocation['Site'][i]] = []
                    sites_involved.append(config.Allocation['Site'][i])
                sites_to_frags[config.Allocation['Site'][i]].append(config.Allocation['Fragment_Name'][i]) 
        
        coordinator.log("begin_commit")
        message_site = {}
        for site in sites_involved:
            abort = 0
            # abort = self.checkSite(site) ##TO BE WRITTEN
            if abort:
                participants[site].log("abort")
                message_site[site] = "Vote-abort"
            else:
                participants[site].log("ready")
                message_site[site] = "Vote-commit"

        unilateral_abort = 0
        for site in message_site:
            if len(message_site[site]) == 10: #got VOTE ABORT
                unilateral_abort = 1
                break
        
        if unilateral_abort:
            coordinator.log("abort")
            
            message = "Global-abort"
            for site in message_site:
                config.debugPrint(message)
                if len(message_site[site]) != 10:
                    # Recieving global abort
                    participants[site].log("abort")
                    participants[site].log("end_of_transaction")
                    participants[site].log("")

            coordinator.log("end_of_transaction")
            coordinator.log("")
        else:
            coordinator.log("commit")
            message = "Global-commit"

            for site in message_site:
                ack = 0
                participants[site].log("commit")

                while ack!=1:
                    # ack = self.handleGlobalCommit(site) ## TO BE WRITTEN
                    tempo = 1

                participants[site].log("end_of_transaction")
                participants[site].log("")

            coordinator.log("end_of_transaction")
            coordinator.log("")
        
        self.finalize()
        return unilateral_abort
