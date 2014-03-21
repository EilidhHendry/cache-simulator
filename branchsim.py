from collections import defaultdict


gccfile = 'gcc_branch.out'
mcffile = 'mcf_branch.out'
testfile = 'gtest.out'

#Some methods for parsing the branches

def getBinBool(line):
    '''Function to get the 0 or 1 bit from a line and make it a boolean.'''
    value = line[-2]
    if value == '1':
        return True
    else:
        return False
    
def getAddress(line):
    '''Function to get the address from a line.'''
    result = line[2:8]
    return result

def getDict(filename):
    '''Function to create a dictionary from the file containing the instructions with the addresses 
    as the keys and the bits (converted to booleans) as values.'''
    dicts = defaultdict(list)
    with open(filename) as tfile:
        for line in tfile:
            dicts[getAddress(line)].append(getBinBool(line))
    return dicts

def getCount(filename):
    '''Returns the number of instructions in a file.'''
    count = 0.0
    with open(filename) as tfile:
        for line in tfile:
            count+=1
    return count


#static prediction

def alwaysTaken(filename):
    '''Function for finding the number of mispredictions using always taken branch prediction.'''
    misprediction = 0
    count = getCount(filename)
    with open(filename) as tfile:
        for line in tfile:
            binBool = getBinBool(line)
            if not(binBool):
                misprediction +=1
    return misprediction*100.0/count

def alwaysNTaken(filename):
    '''Function for finding the number of mispredictions using always not taken branch prediction.'''
    misprediction = 0
    count = getCount(filename)
    with open(filename) as tfile:
        for line in tfile:
            binBool = getBinBool(line)
            if binBool:
                misprediction +=1
    return misprediction*100.0/count

#Helper methods for profile guided prediction

def counts(dicts):
    '''Function which takes a dictionary of addresses as keys and a list of booleans (corresponding to taken or not taken) as values
    and returns the number of time the branch is taken or not taken.
    It stores the counts as tuple pairs in a dictionary with the address as the key and the tuples as values.
    The first value in the tuple is the taken count, the second value is the not taken count.'''
    ndict = {}
    for key, values in dicts.iteritems():
        countTrue = 0.0
        countFalse = 0.0
        for value in values:
            if value == True:
                countTrue+=1.0
            else:
                countFalse+=1.0
        ndict[key] = (countTrue,countFalse)
    return ndict

def percentageTaken(dicts):
    '''Function to calculate the percentage that the address is taken. It takes a dictionary of addresses as keys and tuples of count of taken
    and not taken as values (the outout of the counts method). It returns a dictionary with the addresses as keys and percentage as values.'''
    ndict={}
    for key, (val1,val2) in dicts.iteritems():
        percent = 0
        if val2==0:
            percent = 1.0
        if val1==0:
            percent = 0.0
        else:
            percent = (val1)/(val1+val2)
        ndict[key] = percent
    return ndict

def fileToPercent(filename):
    '''A function that combines the previous two methods and applies them to a file.'''
    dictionary = getDict(filename)
    dictcounts = counts(dictionary)
    result = percentageTaken(dictcounts)
    return result

def profilePredictorTaken(filename):
    '''A function which takes a file and decides if a branch should be taken or not taken depending on whether the branch addresses are taken
    50% or more of the time. Returns a dictionary with the addresses as keys and the taken or not taken (as a boolean) as values.'''
    dicts = {}
    percentDict = fileToPercent(filename)
    for key, value in percentDict.items():
        if value >= 0.5:
            dicts[key] = True
        else:
            dicts[key] = False
    return dicts

def profilePredictorMis(filename):
    '''A function which takes a file and returns the misprediction rate, for profile guided branch prediction, as a percentage.'''
    mispredictions = 0
    noInstructions = getCount(filename)
    realDict = getDict(filename)
    takenDict = profilePredictorTaken(filename)
    for address,boolList in realDict.items():
        for item in boolList:
            if (item != takenDict[address]):
                mispredictions += 1
    return mispredictions*100.0/noInstructions


#Functions for 2-bit branch prediction

def create2Bit(filename):
    '''Function to take a file of branch instructions and set the addresses as keys and the values are initialised as (False, False) which corresponds to 00'''
    newDict = {}
    with open(filename) as tfile:
        for line in tfile:
            newDict[getAddress(line)]=(False,False)
    return newDict 

def findState(boolean,address,bitDict):
    '''Function which takes a boolean, an address, a 2-bit dictionary.

    :param boolean: corresponds to taken or not taken
    :type boolean: bool
    :param address: the address of the instruction
    :type address: str
    :param bitDict: dictionary of addresses and bool tuples
    :type bitDict: dict'''
    if boolean==True:
        if bitDict[address]==(False,False):
            result = bitDict[address]=(False,True)
            return result, 1
        if bitDict[address]==(False,True):
            result = bitDict[address]=(True,False)
            return result, 1
        if bitDict[address]==(True,False):
            result = bitDict[address]=(True,True)
            return result, 0
        if bitDict[address]==(True,True):
            result = bitDict[address]=(True,True)
            return result, 0
    if boolean==False:
        if bitDict[address]==(False,False):
            result = bitDict[address]=(False,False)
            return result, 0
        if bitDict[address]==(False,True):
            result = bitDict[address]=(False,False)
            return result, 0
        if bitDict[address]==(True,False):
            result = bitDict[address]=(False,True)
            return result, 1
        if bitDict[address]==(True,True):
            result = bitDict[address]=(True,False)
            return result, 1
                
def bitPredictor(filename):
    '''Function which takes a file and does 2-bit branch prediction with 0 history and counts the number of mispredictions and returns this as a percentage. '''
    bitDict = create2Bit(filename)
    realDict = getDict(filename)
    noInstructions = getCount(filename)
    mispredictions = []
    for address,boolList in realDict.iteritems():
        for item in boolList:
            a = findState(item,address,bitDict)
            mispredictions.append(a[-1])
            bitDict[address] = a[0]
    missrate = sum(mispredictions)*100.0/noInstructions
    return missrate

def experiments():
    print "Misprediction rates are"
    print "Always Taken gcc_branch.out: ", alwaysTaken(gccfile)
    print "Always Not Taken gcc_branch.out: ", alwaysNTaken(gccfile)
    print "Profile Guided Prediction gcc_branch.out: ", profilePredictorMis(gccfile)
    print "2-Bit Predictor with 0 history gcc_branch.out: ", bitPredictor(gccfile)
    print "Always Taken mcf_branch.out: ", alwaysTaken(mcffile)
    print "Always Not Taken mcf_branch.out: ", alwaysNTaken(mcffile)
    print "Profile Guided Prediction mcf_branch.out: ", profilePredictorMis(mcffile)
    print "2-Bit Predictor with 0 history mcf_branch.out: ", bitPredictor(mcffile)

if __name__ == '__main__':
   experiments()
