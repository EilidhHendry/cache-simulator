from collections import defaultdict

test = 'test.out'

def getRW(line):
    '''Function to get R or W from the instruction.'''
    return line[0]

def getBinBool(line):
    '''Function to get the 0 or 1 bit from a line and make it a boolean.'''
    value = line[-2]
    if value == '1':
        return True
    else:
        return False

def get_address(line):
    '''Function to get the address from a line.'''
    result = line[2:-1]
    return result

def get_trace(filename):
    with open(filename) as tfile:
        return [(getRW(line), get_address(line)) for line in tfile]


def getDict(filename):
    '''Function to create a dictionary from the file containing the instructions with the addresses
    as the keys and the bits (converted to booleans) as values.'''
    dicts = defaultdict(list)
    with open(filename) as tfile:
        for line in tfile:
            dicts[get_address(line)].append(getBinBool(line))
    return dicts

def get_count(filename):
    '''Returns the number of instructions in a file.'''
    count = 0.0
    with open(filename) as tfile:
        for line in tfile:
            count+=1
    return count