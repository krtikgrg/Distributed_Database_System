import config

class takeInput:
    def __init__(self):
        pass
    
    def inputQuery(self):
        '''
        Function to take input from terminal. It accepts input until we encounter a semi-colon(;).
        '''

        config.logger.log("takeInput::inputQuery")

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
