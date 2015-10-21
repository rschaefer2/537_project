__author__ = 'bvschaefer'
import sys

with open(sys.argv[1], 'w') as fin:
    for x in range(30000):
        b = bytearray()
        b.extend("{}".format(x))
        b.extend(bytearray(1024 - len(b)))
        fin.write(str(b))