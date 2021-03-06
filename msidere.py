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
        logging.info(" --> taille du paquet: %s octet(s)", nbytes)
        logging.info(" --> nombre d'echantillons: %s ", nech)
        logging.info(" --> premiere valeur: %s ", val0)
        logging.info(" --> composante continue: %s ", offset)
        logging.info(" --> codes sur : %s bits", nbits)

        # decompression des donnees
        data = datfile.read(16 * nbits)
        datfile.read(nbytes - 10 - 16 * nbits)
        # print(hexlify(data))

        if nbits != 0:
            # donnees en binaire
            data_binaire = bin(int(hexlify(data),
                               16))[2:].rjust(nech * nbits, '0')

            logging.debug("data binaire %s" % data_binaire)
            logging.debug(" len data_binaire %s" % len(data_binaire))

            data_undelta = [data_binaire[i * nbits:(i + 1) * nbits]
                            for i in range(nech)]
            logging.debug(len(data_undelta))
            try:
                data_undelta = [int(x, 2) - offset for x in data_undelta]
            except ValueError:
                logging.warning("erreur lors de la décompression")
                data_undelta = []
            else:
                logging.debug(data_undelta)
                if min(data_undelta) != (- offset):
                    logging.warning('valeur minimum:%s' % min(data_undelta))
                    logging.info(data_undelta)
                data_undelta.insert(0, val0)

        size_block -= nbytes
        data_out.extend(data_undelta)
    return data_out


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="decompression MSIDERE")

    parser.add_argument("filedat", help="fichier sismo.dat")
    parser.add_argument("bloc", help="bloc à décoder")
    parser.add_argument("-l", "--loglevel", help="change the logging level",
                        default="warning",
                        choices=['debug', 'info', 'warning', 'error'])
    args = parser.parse_args()

    numeric_level = getattr(logging, args.loglevel.upper(), None)
    form = '%(levelname)s :: %(asctime)s :: %(message)s'
    logging.basicConfig(level=numeric_level, format=form)

    with open(args.filedat, "rb") as fichier:

        liste_des_bloc = list_bloc(fichier)
        deconfit = decompression(fichier, liste_des_bloc[int(args.bloc)])
        logging.debug("taille data décompressée %s" % len(deconfit))
