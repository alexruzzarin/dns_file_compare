from optparse import OptionParser
import sys, socket
from pprint import pprint
import dns.zone
from dns.exception import DNSException
from dns.rdataclass import *
from dns.rdatatype import *

parser = OptionParser()
parser.add_option("-z", "--zone", dest="zone", metavar="DOMAIN",
	help="name of the domain we're checking (eg: domain.com)")
parser.add_option("-l", "--leftfile", dest="leftzonefile", metavar="LEFTFILE",
	help="zone file to load records from")
parser.add_option("-r", "--rightfile", dest="rightzonefile", metavar="RIGHTFILE",
	help="zone file to load records from")
(opts, remaining_args) = parser.parse_args()

if opts.zone == None or opts.leftzonefile == None or opts.rightzonefile == None:
	print("Error: required arguments: --zone, --leftfile, --rightfile (or --help)")
	sys.exit(-1)

print("Zone:       {0}".format(opts.zone))
print("Left File:  {0}".format(opts.leftzonefile))
print("Right File: {0}".format(opts.rightzonefile))

count = 0
matches = 0
mismatches = 0
notfounds = 0
leftnotfounds = 0
rightnotfounds = 0
foundedNames=[]

def compare(name, expected, result, l2r):
        global count, matches, mismatches, notfounds, leftnotfounds, rightnotfounds
        match = False
        if result == expected:
                match = True
	
        count += 1
        
        if match:
                matches += 1
        else:
                if result == None:
                        status = "NOT FOUND"
                        notfounds += 1
                        if l2r:
                                leftnotfounds += 1
                        else:
                                rightnotfounds += 1
                else:
                        status = "MIS-MATCH"
                        mismatches += 1

                if l2r:
                        direction = ">>>>>>>>>>>>>>>>>>>>>>>>>>>>> L2R"
                else:
                        direction =" <<<<<<<<<<<<<<<<<<<<<<<<<<<<< R2L"    
                print("{0} {1}".format(status, direction))
                print("DOMAIN:   {0}".format(name))
                print("Expected: {0}".format(rdataset))
                print("Received: {0}".format(result))

print("Loading Left File")
lz = dns.zone.from_file(opts.leftzonefile, origin=opts.zone, relativize=False)
print("Loading Right File\n")
rz = dns.zone.from_file(opts.rightzonefile, origin=opts.zone, relativize=False)                
for (name, rdataset) in lz.iterate_rdatasets():
        ans = rz.get_rdataset(name, rdataset.rdtype)
        if ans != None:
                foundedNames.append(name)

        compare(name, rdataset, ans, True)

#tranformo el list en un set por performance
foundedNames = set(foundedNames)

for (name, rdataset) in rz.iterate_rdatasets():
        if name in foundedNames:
                continue
        #No es necesario volver a buscar, por que es cierto que no esta.
        #ans = lz.get_rdataset(name, rdataset.rdtype)
        #compare(name, rdataset, ans, False)
        compare(name, rdataset, None, False)


print("DONE\n")

print("Zone:       {0}".format(opts.zone))
print("Left File:  {0}".format(opts.leftzonefile))
print("Right File: {0}".format(opts.rightzonefile))
print("\nResults:")
print("Count:            {0}".format(count))
print("Matches:          {0}".format(matches))
print("Mis-matches:      {0}".format(mismatches))
print("Total Not founds: {0}".format(notfounds))
print("Left Not founds:  {0}".format(leftnotfounds))
print("Right Not founds: {0}".format(rightnotfounds))
