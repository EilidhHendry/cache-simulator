from collections import defaultdict

test = 'test.out'

def get_rw(line):
    '''Function to get R or W from the instruction.'''
    return line[0]

def get_address(line):
    '''Function to get the address from a line.'''
    result = line[2:-1]
    return result

def get_trace(filename):
    with open(filename) as tfile:
        return [(get_rw(line), get_address(line)) for line in tfile]
