# projet Mseedifie
# partie decompression donnees 

import binascii
import struct
from binascii import hexlify, unhexlify
from struct import pack, unpack

with open("masseData.dat", "rb") as fichier:
	size_block = unhexlify(fichier.read(4))
	size_block=hexlify(pack('<h', *unpack('>h', size_block)))

	fichier.read(1)

	size_paquet = unhexlify(fichier.read(4))
	size_paquet=hexlify(pack('<h', *unpack('>h', size_paquet)))

	texte = fichier.read(int(size_paquet, 16)*2)




print 'taille du block', int(size_block, 16), 'octet(s)'
print 'taille du paquet', int(size_paquet, 16), 'octet(s)'

print 'donnees du premier paquet :\n' , texte
