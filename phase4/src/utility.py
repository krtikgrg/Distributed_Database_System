import paramiko
from scp import SCPClient
import config

def dumpTable(relname,siteno,ofile = 'dump.txt'):
    '''
    Function which will dump a mysql table using mysqldump command into ofile
    '''
    config.logger.log("utility::dumpTable")
    
    command = "echo 'use "+config.catalogName+";' > ./Outlaws/"+ofile
    (a,b,c) = config.paramikoConnections[siteno].exec_command(command)
    op = c.read()

    command = "mysqldump -u user -piiit123 "+config.catalogName+" "+relname+" >> ./Outlaws/"+ofile
    # print(command)
    (a,b,c) = config.paramikoConnections[siteno].exec_command(command)
    op = c.read()
    # print(op)

def copyFromServer(siteno,ofile = 'dump.txt'):
    '''
    Function to copy a file from the Server to my machine
    '''
    config.logger.log("utility::copyFromServer")

    with SCPClient(config.paramikoConnections[siteno].get_transport()) as scp:
        scp.get("./Outlaws/"+ofile,ofile)

def copyToServer(siteno,ofile = 'dump.txt'):
    '''
    Function to copy a file from my machine to Server
    '''
    config.logger.log("utility::copyToServer")

    with SCPClient(config.paramikoConnections[siteno].get_transport()) as scp:
        scp.put(ofile,"./Outlaws/"+ofile)

def importTable(siteno,ofile = 'dump.txt'):
    '''
    Function to read the dump.txt file
    '''
    config.logger.log("utility::importTable")

    command = "mysql -u user -piiit123 < ./Outlaws/"+ofile
    (a,b,c) = config.paramikoConnections[siteno].exec_command(command)
    op = c.read()