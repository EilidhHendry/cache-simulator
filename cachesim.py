import sys
import os
from math import log
from parse import *

gcc = 'gcc_memref.out'

class Cache(object):
    def __init__(self, n_ways=1, block_size=32, n_blocks=128, address_size=48):
        self.cache_size = block_size * n_blocks * n_ways  # in bytes
        self.block_size = block_size  # size of each block in bytes
        self.address_size = address_size  # in bytes
        self.n_blocks = n_blocks  # number of blocks in the cache.
        self.n_ways = n_ways  # 1 for direct mapping. 2 for sets if size 2, etc.
        self.offset_size = int(log(block_size, 2))
        self.index_size = int(log(self.n_blocks, 2))
        self.tag_size = address_size - self.offset_size - self.index_size

        # miss rates
        self.r_misses = 0
        self.w_misses = 0

        # number of read/write operations
        self.n_read = 0
        self.n_write = 0

        self.cache = {}

    def decode(self, address):
        ''' Method to decode the raw memory address into it's tag, index and offset.
        '''
        bits = bin(int(address, 16))  # get the address in bits
        bits = bits.zfill(self.address_size)  # add padding until its the correct size
        offset = bits[-self.offset_size:]  # find the offset bits
        tag = bits[:self.tag_size]  # find the tag bits 
        index = bits[self.tag_size:self.index_size + self.tag_size]  # find the index bits
        return tag, index, offset

    # TODO change to miss?
    def store(self, address):
        ''' Method that handles a cache miss. It increments the lru values and removes the lru block if the set is full.
        '''
        tag, index, offset = self.decode(address)
        # returns the cache set at the index or creates an empty dict at the index if not there
        cache_set = self.cache.setdefault(index, {})
        # Check that the cache set is smaller than the number of sets that should be in it
        if len(cache_set) < self.n_ways:
            # if the cache set is not empty then add 1 to the value
            if tag in cache_set:
                cache_set[tag] += 1
            # if the cache set is empty then set the tag value to 1
            else:
                cache_set[tag] = 1
        else:
            # the lru block is the block with the min lru value
            lru = min(cache_set.iterkeys(), key=lambda k: cache_set[k])
            # delete the lru block
            del cache_set[lru]
            # if the cache set is not empty then add 1 to the value
            if tag in cache_set:
                cache_set[tag] += 1
            # if the cache set is empty then set the tag value to 1
            else:
                cache_set[tag] = 1
        # Checks the length of the cache set is less than or equal to the no of ways
	assert len(cache_set) <= self.n_ways


    def increment_lru(self, address):
        ''' Method to increase the lru value of a block on the event of a hit.
        '''
        tag, index, offset = self.decode(address)
        cache_set = self.cache[index]
        if len(cache_set) < self.n_ways:
            	# if the cache set is not empty then add 1 to the value
            if tag in cache_set:
                cache_set[tag] += 1
            	# if the cache set is empty then set the tag value to 1
            else:
                cache_set[tag] = 1

    def is_cache_hit(self, address):
        ''' Method to check if an address is already stored in the cache (a hit).
        '''
        tag, index, offset = self.decode(address)
        if index in self.cache:
            cache_set = self.cache[index]
            if tag in cache_set:
                return True
        return False

    def read_write(self, op, address):
        ''' Method
        '''
        if self.is_cache_hit(address):
            self.increment_lru(address)
        else:
            self.store(address)
            # Check if the number of items currently in the cache is less than the number of sets in the cache
            # Else
            if op == 'R':
                self.r_misses += 1
            elif op == 'W':
                self.w_misses += 1
        # Regardless of whether there is a cache hit or not increment the read/write count
        if op == 'R':
            self.n_read += 1
        elif op == 'W':
            self.n_write += 1

    def _reset(self):
        self.cache = {}
        self.n_read = 0
        self.n_write = 0
        self.r_misses = 0
        self.w_misses = 0

    def simulate(self, filename):
        '''
        '''
        # Checks if the cache is empty and resets it if it's not.
	if self.cache:
		self._reset()

        # Takes the tracefile and gets a list of tuples of the operation and address.
        tracelist = get_trace(filename)
        
        # Loops through the trace list and 
        # Also checks that the length of the cache is never bigger than it should be
        for (op, address) in tracelist:
        	self.read_write(op, address)
		assert len(self.cache) <= self.n_blocks
        
        # Calculate result values
        tot_misses = self.r_misses + self.w_misses
        tot_ops = self.n_write + self.n_read
        total_missrate = tot_misses / (tot_ops * 1.0)
        write_missrate = self.w_misses / (self.n_write * 1.0)
        read_missrate = self.r_misses / (self.n_read * 1.0)

        #REMOVE
	assert all([len(s) <= self.n_ways
                   for s in self.cache.itervalues()])
        assert tot_ops == len(tracelist)

        # Dictionary containing the results
        results = dict(
            cache_size=self.cache_size / 1024,
            n_ways=self.n_ways,
            n_sets=self.n_blocks,
            total_missrate=total_missrate,
            write_missrate=write_missrate,
            read_missrate=read_missrate,
            trace_file=filename,
        )
        return results


def run():
    simulate_all('mcf_memref.out', 'testout.json')


def test_caches():
    m_range = [1, 2, 4, 8, 16]
    n_ways = [1, 2, 4, 8, 16]
    caches = [Cache(n_blocks=128 / k * i, n_ways=k) for i in m_range for k in n_ways]
    return caches


def simulate_all(infile, outfile):
    import json

    caches = test_caches()
    results = [c.simulate(infile) for c in caches]
    with open(outfile, 'w') as o:
        j = json.dump(results, o, indent=4)


if __name__ == "__main__": run()
