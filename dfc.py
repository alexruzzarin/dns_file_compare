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
	print("Error: required arguments: --leftfile, --rightfile (or --help)")
	sys.exit(-1)
	
lz = dns.zone.from_file(opts.leftzonefile, origin=opts.zone, relativize=False)
rz = dns.zone.from_file(opts.rightzonefile, origin=opts.zone, relativize=False)

count = 0
matches = 0
mismatches = 0
foundedNames=[]

for (name, rdataset) in lz.iterate_rdatasets():
	#print(name, rdataset.rdtype, rdataset.rdclass, sep=", ")
	match = False
	result = None
	
	ans = rz.get_rdataset(name, rdataset.rdtype)
	if ans != None:
		foundedNames.append(name)
	
	result = ans
	if result == rdataset:
		match = True
	
	count += 1
	if match:
		matches += 1
	else:
		mismatches += 1
		print(">>>>>>>>>>>>>>>>>>")
		print("(%s) query: %s ..." % ("MIS-MATCH", name))
		print("Expected: ", rdataset)
		print("Received: ", result)
		
for (name, rdataset) in rz.iterate_rdatasets():
	if name in foundedNames:
		continue

	#print(name, rdataset.rdtype, rdataset.rdclass, sep=", ")
	match = False
	result = None
	
	ans = lz.get_rdataset(name, rdataset.rdtype)
	if ans != None:
		foundedNames.append(name)
	
	result = ans
	if result == rdataset:
		match = True
	
	count += 1
	if match:
		matches += 1
	else:
		mismatches += 1
		print("<<<<<<<<<<<<<<<<<<")
		print("(%s) query: %s ..." % ("MIS-MATCH", name))
		print("Expected: ", rdataset)
		print("Received: ", result)

		
		
print("done")

print("\nResults:")
print("Count:     ", count)
print("Matches:     ", matches)
print("Mis-matches: ", mismatches)

	