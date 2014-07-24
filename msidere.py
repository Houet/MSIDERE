# projet Mseedifie
# partie decompression donnees 

import os
import logging
import binascii
import struct
from binascii import hexlify, unhexlify
from struct import pack, unpack



def function_logging(loglevel):
    """ module logging """

    numeric_level = getattr(logging, loglevel.upper(), None)
    form = '%(levelname)s :: %(asctime)s :: %(message)s'
    logging.basicConfig(level=numeric_level, format=form)
    return

def decompression():
    """ vide """


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="decompression MSIDERE")

    parser.add_argument("-l", "--loglevel", help="change the logging level", 
        default="warning", choices=['debug', 'info', 'warning', 'error'])
    args = parser.parse_args()


    function_logging(args.loglevel)






##########################  demarrage du code  ############################  


    with open("sismo.dat", "rb") as fichier:


        ############################## exemple ##############################
        # try:                                                              #
        #   s = struct.Struct(">hhhhhh")                                    #
        #   record = fichier.read(12)                                       #               
        #   nblock, nbytes, nech, val0, offset, nbits = s.unpack(record)    #
        #   record = pack(">h", nblock)                                     #
        # except IOError:                                                   #
        #   pass                                                            #
        #####################################################################

        try:
            #on lis la taille du block
            size_block = pack(">h", *unpack("<h", fichier.read(2)))
            free_block = int(hexlify(size_block), 16)
            logging.info("taille du block: %s octet(s)", free_block)

            #on lis les paquets
            while free_block > 0:
                s = struct.Struct("<hhhhh")
                record = fichier.read(10)
                nbytes, nech, val0, offset, nbits = s.unpack(record)
                logging.info("taille du paquet: %s octet(s)", nbytes)

                #decompression des donnees

                data = fichier.read(nbytes - 10)


                #donnees en binaire
                data_binaire = bin(int(hexlify(data),16))[2:]
                size_data = range(len(data_binaire)/nbits)

                data_undelta = ['0'*(16 - nbits) + data_binaire[i*nbits:(i + 1)*nbits] for i in size_data]
                data_undelta = ''.join(data_undelta)
                
                with open("dest.dat", "ab") as dest:
                    dest.write("\n\n ***** NOUVEAU PAQUET ***** \n\n")
                    dest.write("donnees non decompressee en binaire\n\n")
                    dest.write(data_binaire)
                    dest.write("\n\ndonnees decompressee en binaire\n\n")
                    dest.write(data_undelta)

                #free_block = 0
                free_block -= nbytes

        except IOError:
            pass

    os.system("vi dest.dat")
    #os.system("od -x dest.dat")



############################  commentaires #################################


# pour l'instant on ne lis que le premier paquet pour se simplifier la tache
# on a aussi reutiliser la meme structure que celle utilise en C precedemment 
# par mr Frogneux