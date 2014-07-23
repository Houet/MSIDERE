# projet Mseedifie
# partie decompression donnees 

import binascii
import struct
from binascii import hexlify, unhexlify
from struct import pack, unpack


with open("sismo.dat", "rb") as fichier:

	try:
		s = struct.Struct(">6h")
		record = fichier.read(12)
		paquet = s.unpack(record)
		record = s.pack(*paquet)
	except IOError:
		pass

with open("dest.dat", "wb") as dest:
	dest.write(record)


print 'finis !'
