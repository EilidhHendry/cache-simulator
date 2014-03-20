from cachesim import *
from pprint import pprint
import sys
import os

def main():
    print 'Welcome to my cache simulator. Please wait while your results are calculated.'
    
    if not len(sys.argv) == 6: # Check for command line arguments
        print "Usage: %s [ n-ways ] [ block size ] [ n-sets] [ address-size ] [ filename ]\n" % \
            os.path.basename(sys.argv[0])
        sys.exit(0)
    
    n_ways = int(sys.argv[1])
    block_size = int(sys.argv[2])
    n_sets = int(sys.argv[3])
    address_size = int(sys.argv[4])
    testfile = sys.argv[5]
    
    cache = Cache(n_ways=n_ways,block_size=block_size,n_blocks=n_sets,address_size=address_size)
    results = cache.simulate(testfile)
    pprint(results)

if __name__ == '__main__':
    main()
    
