import config
import pandas as pd
import mysql
from mysql.connector import Error
import copy
from utility import dumpTable,copyToServer,importTable

class TakeInput:
    '''
    Class responsible for taking inputs.
    '''
    def __init__(self):
        config.logger.log("TakeInput::Constructor")
        pass
    
    def inputQuery(self):
        '''
        Function to take queries as input from terminal. It accepts input until we encounter a semi-colon(;).
        '''

        config.logger.log("TakeInput::inputQuery")

        inputString = ""
        currentLine = ""

        while(len(currentLine) == 0):
            currentLine = input("->> ")
            currentLine = currentLine.strip()

        while(len(currentLine)==0 or currentLine[-1] != ";"):
            inputString += currentLine
            inputString += ' '
            
            currentLine = input(".... ")
            currentLine = currentLine.strip()

        # currentLine = currentLine[:-1] # Last semicolon will be removed
        # Last semi-colon is not removed if above line is commented
        inputString += currentLine
        inputString = ' '.join(inputString.split()) # Multiple spaces removed
        inputString = inputString.strip()

        config.debugPrint(inputString)
        return inputString

    def createF(self,splitted,site,connection,cursor,fragmentName):
        '''
        Function to actually create a HF and a VF and ship it to a site
        '''
        config.logger.log("Input::createF")

        index = splitted.index("from")
        if splitted[index+1].find('.') == -1:
            splitted[index+1] = config.catalogName+"."+splitted[index+1]
        # config.logger.log("Input::createHF")
        # curcommand = "USE zomato_catalog_outlaws;"
        curcommand ="CREATE TABLE "+config.catalogName+"."+fragmentName+" " 
        curcommand += (' '.join(splitted))
        curcommand += ";"
        # curse = connection.cursor()
        try:
            cursor.execute(curcommand)
            # result = cursor.fetchall()
        except Error as e:
            print("Reached an error on",curcommand,"therefore exiting..")
            print(e)
            exit()
        connection.commit()
        # curse.close()
        #export the created relation to the site
        dumpTable(fragmentName,-1,'dump.txt',1)
        copyToServer(site)
        importTable(site)    

    def createDHF(self,splitted,site,connection,cursor,fragmentName):
        '''
        Function to actually create a DHF and ship it to a site
        '''
        config.logger.log("Input::createDHF")

        index = splitted.index("from")
        concernedRel = ""
        if splitted[index+1].find('.') == -1:
            concernedRel = copy.deepcopy(splitted[index+1])
            splitted[index+1] = config.catalogName+"."+splitted[index+1]
        else:
            concernedRel = copy.deepcopy(splitted[index+1][:splitted[index+1].find('.')])
        index = splitted.index("JOIN")
        if splitted[index+1].find('.') == -1:
            splitted[index+1] = config.catalogName+"."+splitted[index+1]

        splitted[1] = ""
        for i in range(len(config.Columns['Table_Name'])):
            if config.Columns['Table_Name'][i] == concernedRel:
                splitted[1] = splitted[1] + config.Columns['Column_Name'][i]+","
        splitted[1] = splitted[1][:-1]
        # config.logger.log("Input::createHF")
        # curcommand = "USE zomato_catalog_outlaws;"
        curcommand ="CREATE TABLE "+config.catalogName+"."+fragmentName+" " 
        curcommand += (' '.join(splitted))
        curcommand += ";"
        # curse = connection.cursor()
        try:
            cursor.execute(curcommand)
            # result = cursor.fetchall()
        except Error as e:
            print("Reached an error on",curcommand,"therefore exiting..")
            print(e)
            exit()
        connection.commit()
        # curse.close()
        #export the created relation to the site
        dumpTable(fragmentName,-1,'dump.txt',1)
        copyToServer(site)
        importTable(site)  

    def handleFragments(self,path,connection,cursor):
        '''
        Function to read the files corresponding to the fragments
        '''
        config.logger.log("Input::handleFragments")

        data = []
        with open(path,'r') as fp:
            data = fp.readlines()
        nuData = ""
        for line in data:
            if line[:2] == "--":
                continue
            if line[-1] == '\n':
                nuData = nuData+line[:-1]+" "
            else:
                nuData = nuData+line+" "
        nuData = nuData[:-1]
        nuData = nuData.split(";")

        for command in nuData:
            splitted = command.split()
            if len(splitted) == 0:
                continue
            if splitted[1] == "*":
                # either HF or DHF
                concernedRel = splitted[3]
                site = int(splitted[-1])
                fragmentName = splitted[-3]
                condition = copy.deepcopy(splitted[5:-4])
                config.Allocation['Fragment_Name'].append(fragmentName)
                config.Allocation['Site'].append(site)
                if 'JOIN' not in splitted:
                    attribute = condition[0]
                    operator = condition[1]
                    value = None
                    if condition[2].isnumeric():
                        value = int(condition[2])
                    else:
                        value = condition[2][1:-1]
                    config.Horizontal_Fragments['Fragment_Name'].append(fragmentName)    
                    config.Horizontal_Fragments['Table_Name'].append(concernedRel)    
                    config.Horizontal_Fragments['Attribute'].append(attribute)    
                    config.Horizontal_Fragments['Operator'].append(operator)    
                    config.Horizontal_Fragments['Val'].append(value)
                    self.createF(splitted[:-4],site,connection,cursor,fragmentName)
                else:
                    config.Derived_Horizontal_Fragments['Fragment_Name'].append(fragmentName)
                    config.Derived_Horizontal_Fragments['Table_Name'].append(concernedRel)
                    config.Derived_Horizontal_Fragments['Horizontal_Fragment_Name'].append(copy.deepcopy(condition[1]))
                    if condition[1] in config.Horizontal_Fragments['Fragment_Name']:
                        config.Derived_Horizontal_Fragments['Direct_Fragment'].append(1)
                    else:
                        config.Derived_Horizontal_Fragments['Direct_Fragment'].append(0)
                    # self.createDHF(concernedRel,fragmentName,copy.deepcopy(condition[0]),site,connection,cursor)
                    self.createDHF(splitted[:-4],site,connection,cursor,fragmentName)
            else:
                #VF
                site = int(splitted[-1])
                fragmentName = splitted[-3]
                concernedRel = splitted[-5]
                config.Allocation['Fragment_Name'].append(fragmentName)
                config.Allocation['Site'].append(site)
                columns_current = splitted[1:-6]
                columns_current = ''.join(columns_current)
                columns_current = columns_current.split(',')
                config.Vertical_Fragments['Fragment_Name'].append(fragmentName)
                config.Vertical_Fragments['Table_Name'].append(concernedRel)
                for acolumn in columns_current:
                    config.VF_Columns['Fragment_Name'].append(fragmentName)
                    config.VF_Columns['Column_Name'].append(acolumn)
                self.createF(splitted[:-4],site,connection,cursor,fragmentName)

            ## ACTUALLY EXECUTE AND CREATE FRAGMENTS

    def insertData(self,path,connection,cursor):
        '''
        Function to insert data in my local machine
        '''
        config.logger.log("Input::insertData")

        data = []
        with open(path,'r') as fp:
            data = fp.readlines()
        nuData = ""
        for line in data:
            if line[:2] == "--":
                continue
            if line[-1] == '\n':
                nuData = nuData+line[:-1]+" "
            else:
                nuData = nuData+line+" "
        nuData = nuData[:-1]
        nuData = nuData.split(";")

        for command in nuData:
            splitted = command.split()
            if len(splitted) == 0:
                continue
            if splitted[0] == 'INSERT' and splitted[1] == 'INTO':
                if splitted[2].find('.') == -1:
                    splitted[2] = config.catalogName+'.'+splitted[2]
            curcommand = ' '.join(splitted)
            curcommand += ";"
            try:
                cursor.execute(curcommand)
            except:
                print("Reached an error on",curcommand,"therefore exiting..")
                exit()
            connection.commit()
        # print("No errors, and now check data in mysql")
        # exit()

    def initializeSites(self):
        '''
        Fucntion to drop the database if already existing
        '''
        config.logger.log("Input::initializeSites")

        with open("temp.sql",'w') as fp:
            fp.write("DROP DATABASE IF EXISTS "+config.catalogName+";\n")
            fp.write("CREATE SCHEMA "+config.catalogName)
        for site in config.available_sites:
            copyToServer(site,'temp.sql')
            command = "mysql -u user -piiit123 < ./Outlaws/temp.sql"
            (a,b,c) = config.paramikoConnections[site].exec_command(command)
            op = c.read()
        # exit()

    def inputSchema(self):
        '''
        Function to take sql queries as input which will describe the schema
        '''
        config.logger.log("TakeInput::inputSchema")
        #pending

        #make connection to local mysql
        connection = mysql.connector.connect(host='localhost',user=config.localuser,password=config.localpass)
        cursor = connection.cursor()

        #Application DBMS
        path = config.PATH_TO_SCHEMAS+"Application.sql"
        data = []
        with open(path,'r') as fp:
            data = fp.readlines()
        nuData = ""
        for line in data:
            if line[:2] == "--":
                continue
            if line[-1] == '\n':
                nuData = nuData+line[:-1]+" "
            else:
                nuData = nuData+line+" "
        nuData = nuData[:-1]
        nuData = nuData.split(";")

        for command in nuData:
            splitted = command.split()
            if len(splitted) == 0:
                continue
            if len(splitted) == 2 and (splitted[0].upper() == "USE"):
                config.catalogName = splitted[1]
            elif len(splitted) == 3 and (splitted[0].upper() == "CREATE" and splitted[1].upper() == "SCHEMA"):
                config.catalogName = splitted[2]
            elif len(splitted)>=2 and splitted[0].upper() == 'CREATE' and splitted[1].upper() == 'TABLE':
                if splitted[2].find(".") == -1:
                    config.all_tables.append(splitted[2])
                    splitted[2] = config.catalogName+"."+splitted[2]
                else:
                    config.all_tables.append(splitted[2][splitted[2].find('.')+1:])
            curcommand = ' '.join(splitted)
            curcommand += ";"
            try:
                cursor.execute(curcommand)
            except:
                print(curcommand)
                exit()
            connection.commit()
        # print(config.all_tables)

        config.TableKeys = {}
        for table in config.all_tables:
            sqlQuery = "select COLUMN_NAME from information_schema.COLUMNS where TABLE_SCHEMA='"+config.catalogName+"' and TABLE_NAME='"+table+"' and COLUMN_KEY='PRI'"
            tempo = pd.read_sql_query(sqlQuery,connection)
            tempo = list(tempo['COLUMN_NAME'])
            tempo = tempo[0]
            config.TableKeys[table] = tempo
        # print(config.TableKeys)

        config.Columns = {
            'Table_Name':[],
            'Column_Name':[]
        }
        for table in config.all_tables:
            sqlQuery = "select COLUMN_NAME from information_schema.COLUMNS where TABLE_SCHEMA='"+config.catalogName+"' and TABLE_NAME='"+table+"'"
            tempo = pd.read_sql_query(sqlQuery,connection)
            tempo = list(tempo['COLUMN_NAME'])
            for column in tempo:
                config.Columns['Table_Name'].append(table)
                config.Columns['Column_Name'].append(column)
        # print(config.Columns)

        ##  INSERT DATA Pending
        self.insertData(config.PATH_TO_SCHEMAS+"data.sql",connection,cursor)
        self.initializeSites()

        config.Horizontal_Fragments = {
            'Fragment_Name':[],
            'Table_Name':[],
            'Attribute':[],
            'Operator':[],
            'Val':[]
        }
        config.Derived_Horizontal_Fragments = {
            'Table_Name':[],
            'Fragment_Name':[],
            'Horizontal_Fragment_Name':[],
            'Direct_Fragment':[]
        }
        config.Vertical_Fragments = {
            'Fragment_Name':[],
            'Table_Name':[]
        }
        config.VF_Columns = {
            'Fragment_Name':[],
            "Column_Name":[]
        }
        config.Allocation = {
            'Fragment_Name':[],
            'Site':[]
        }
        # for x in config.available_sites:
        self.handleFragments(config.PATH_TO_SCHEMAS+"fragmentation.sql",connection,cursor)

        config.Tables = {
            'Name':[],
            'Fragmentation_Type':[],
            'Number_Of_Fragments':[]
        }
        for table in config.all_tables:
            if table in config.Horizontal_Fragments['Table_Name']:
                config.Tables['Name'].append(table)
                config.Tables['Fragmentation_Type'].append('HF')
                config.Tables['Number_Of_Fragments'].append(config.Horizontal_Fragments['Table_Name'].count(table))
            elif table in config.Derived_Horizontal_Fragments['Table_Name']:
                config.Tables['Name'].append(table)
                config.Tables['Fragmentation_Type'].append('DHF')
                config.Tables['Number_Of_Fragments'].append(config.Derived_Horizontal_Fragments['Table_Name'].count(table))
            elif table in config.Vertical_Fragments['Table_Name']:
                config.Tables['Name'].append(table)
                config.Tables['Fragmentation_Type'].append('VF')
                config.Tables['Number_Of_Fragments'].append(config.Vertical_Fragments['Table_Name'].count(table))
            else:
                config.Tables['Name'].append(table)
                config.Tables['Fragmentation_Type'].append(None)
                config.Tables['Number_Of_Fragments'].append(0)

        # path = config.PATH_TO_SCHEMAS+"fragmentation_1.sql"
        # print('Horizontal_Fragments',config.Horizontal_Fragments)
        # print()
        # print('Derived_Horizontal_Fragments',config.Derived_Horizontal_Fragments)
        # print()
        # print('Vertical_Fragments',config.Vertical_Fragments)
        # print()
        # print('VF_Columns',config.VF_Columns)
        # print()
        # print('Allocation',config.Allocation)
        # print()
        # print('Tables',config.Tables)
        # print()
        # print("All tables",config.all_tables)
        # print()
        # print("catalog name",config.catalogName)
        # print()
        # print("Table keys",config.TableKeys)
        # print()
        # print("Columns",config.Columns)
        # print()
        # exit()