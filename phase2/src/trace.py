import config
class logger:
    def __init__(self):
        self.PATH = config.PATH_TO_LOGS_FILE
        self.fp = open(self.PATH,'w')

    def log(self,str):
        '''
        This function writes the string mentioned in str in the log file whoose path
        is mentioned in config file.
        '''
        self.fp.write(str)
        self.fp.write('\n')
        self.fp.flush()