import config
def generateRelationColumnMapFromMetaData():
    '''
    Function to generate the relationColumnMap from the read metadata through csv/sql
    csv/sql reading is yet to be done
    '''
    config.logger.log("preprocess::generateRelationColumnMapFromMetaData")
    config.relationColumnMap = {}
    for i in range(len(config.Columns['Table_Name'])):
        if config.Columns['Table_Name'][i] not in config.relationColumnMap:
            config.relationColumnMap[config.Columns['Table_Name'][i]] = []
        config.relationColumnMap[config.Columns['Table_Name'][i]].append(config.Columns['Column_Name'][i])