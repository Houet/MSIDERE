#!/usr/bin/env python
# -*- coding=utf-8 -*-


# ##### partie decompression des données

import os
import logging
import binascii
from matplotlib import pyplot as plt
from binascii import hexlify, unhexlify
import struct
from struct import pack, unpack


def list_bloc(datfile):
    """ """
    list_bloc = []
    while True:
        try:
            bloc_begin = datfile.tell()
            size_block, =  unpack("h", datfile.read(2))
        except struct.error:
            break
        else:
            list_bloc.append((bloc_begin, size_block))
            datfile.seek(list_bloc[-1][0] + list_bloc[-1][1] + 2)
    return list_bloc


def decompression(datfile, bloc):
    """ vide """

    datfile.seek(bloc[0])
    data_out = []
    # on lis la taille du block
    size_block, = unpack("h", datfile.read(2))
    logging.info("taille du block: %s octet(s)", size_block)

    # on lis les paquets
    while size_block > 0:
        s = struct.Struct("5h")
        nbytes, nech, val0, offset, nbits = s.unpack(datfile.read(10))
        logging.debug(" --> taille du paquet: %s octet(s)", nbytes)
        logging.debug(" --> nombre d'echantillons: %s ", nech)
        logging.debug(" --> premiere valeur: %s ", val0)
        logging.debug(" --> composante continue: %s ", offset)
        logging.debug(" --> codes sur : %s bits", nbits)

        # decompression des donnees
        data = datfile.read(nbytes - 10)
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

        size_block -= nbytes
        data_out.extend(data_undelta)
    return data_out


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="decompression MSIDERE")

    parser.add_argument("-l", "--loglevel", help="change the logging level",
                        default="warning",
                        choices=['debug', 'info', 'warning', 'error'])
    parser.add_argument("bloc", help="bloc à décoder")
    args = parser.parse_args()

    numeric_level = getattr(logging, args.loglevel.upper(), None)
    form = '%(levelname)s :: %(asctime)s :: %(message)s'
    logging.basicConfig(level=numeric_level, format=form)


    with open("sismo.dat", "rb") as fichier:

        liste_des_bloc = list_bloc(fichier)
        deconfit = decompression(fichier, liste_des_bloc[int(args.bloc)])
        logging.info(len(deconfit))

    plt.plot(deconfit)
    plt.show()



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
