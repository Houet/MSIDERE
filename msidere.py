#!/usr/bin/env python
# -*- coding=utf-8 -*-


# ##### partie decompression des données

import os
import logging
import binascii
from binascii import hexlify, unhexlify
import struct
from struct import pack, unpack


def decompression(fichier, fichierdest, iterateur):
    """ vide """

    # on lis la taille du block
    try:
        size_block, = unpack("h", fichier.read(2))
    except struct.error:
        logging.warning('fin du fichier, nombre de block : %s', iterateur)
        return False
    else:
        logging.info("taille du block: %s octet(s)", size_block)

        # on lis les paquets
        while size_block > 0:
            s = struct.Struct("5h")
            nbytes, nech, val0, offset, nbits = s.unpack(fichier.read(10))
            logging.debug(" --> taille du paquet: %s octet(s)", nbytes)
            logging.debug(" --> nombre d'echantillons: %s ", nech)
            logging.debug(" --> premiere valeur: %s ", val0)
            logging.debug(" --> composante continue: %s ", offset)
            logging.debug(" --> codes sur : %s bits", nbits)

            # decompression des donnees
            data = fichier.read(nbytes - 10)
            # print(hexlify(data))

            if nbits != 0:
                # donnees en binaire
                data_binaire = bin(int(hexlify(data), 16))[2:]

                data_undelta = [data_binaire[i * nbits:(i + 1) * nbits]
                                for i in range(nech)]
                logging.debug(len(data_undelta))
                data_undelta = [int(x, 2) - offset for x in data_undelta]
                logging.debug(data_undelta)
                data_undelta.insert(0, val0)

                # reencodage
                data_out = [pack('h', i) for i in data_undelta]

                # print data_out
                with open(fichierdest, "ab") as decompress:
                    for i in data_out:
                        decompress.write(i)

            size_block -= nbytes
        return True


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="decompression MSIDERE")

    parser.add_argument("-l", "--loglevel", help="change the logging level",
                        default="warning",
                        choices=['debug', 'info', 'warning', 'error'])
    parser.add_argument("-f", "--fichierdest",
                        help="fichier de destination de la decompression",
                        default="decompress.dat")
    parser.add_argument("-b", "--bloc", help="nombre de bloc à décoder")
    args = parser.parse_args()

    numeric_level = getattr(logging, args.loglevel.upper(), None)
    form = '%(levelname)s :: %(asctime)s :: %(message)s'
    logging.basicConfig(level=numeric_level, format=form)


# #########################  demarrage du code  ############################

    with open("sismo.dat", "rb") as fichier:

        # ############################# exemple ##############################
        # try:                                                              #
        #   s = struct.Struct(">hhhhhh")                                    #
        #   record = fichier.read(12)                                       #
        #   nblock, nbytes, nech, val0, offset, nbits = s.unpack(record)    #
        #   record = pack(">h", nblock)                                     #
        # except IOError:                                                   #
        #   pass                                                            #
        # ####################################################################

        i = 0
        if not args.bloc: 
            while decompression(fichier, args.fichierdest, i):
                i += 1
        else:
            while i < int(args.bloc):
                decompression(fichier, args.fichierdest, i)
                logging.debug(fichier.tell())
                i += 1

# ###########################  commentaires #################################


# pour l'instant on ne lis que le premier paquet pour se simplifier la tache
# on a aussi reutiliser la meme structure que celle utilise en C precedemment
# par mr Frogneux


# edit :
# on lis tous les paquets du block maintenant, qu'on convertis en binaire
# pour pouvoir separer les bits lorsque nbits car nbits est souvent pas
# multiple d'un octet
# on pack ensuite dans le fichier decompress.dat apres avoir
# retranche la composante continue et ajoute la premiere valeur val0
# pour l'instant on ne travaille que sur un seul block

# edit 1 aout:
# on essai de lire tous les blocks a l'aide d'un retour en booleen on
# arrete quand tous les blocks ont ete lus ie quand false est renvoyé par
# la focntion decompression

# edit 4 aout:
# bug trouvé sur la division qui en fait renvoi un resultat entier (mtnt float)
# petit probleme au niveau du nombre de bits qu'on doit lire
# soit 896 soit 928 selon les versions
# peut etre signal de fin de paquet avec les 8 zeros encodés en fait de paquets

# on prends que 128 premieres valeur et on considere que les derniers zero
# c'est une sorte de signal de fin
# et on continue la ou on s'etait arrete
