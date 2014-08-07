#!/usr/bin/env python
# -*- coding=utf-8 -*-


# ##### partie lecture du fichier sismo.cat

import os
import logging
import binascii
from binascii import hexlify, unhexlify
import struct
from struct import pack, unpack
from time import gmtime, strftime
import numpy as np
from matplotlib import pyplot as plt
from obspy.core import read, Trace, Stream, UTCDateTime

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


def decompression(datfile, offset_bloc):
    """ vide """

    datfile.seek(offset_bloc)
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
    parser = argparse.ArgumentParser(description="lecture de sismo.cat")

    parser.add_argument("-l", "--loglevel", help="change the logging level",
                        default="info",
                        choices=['debug', 'info', 'warning', 'error'])
    parser.add_argument("bloc", help="nombre de minutes à décoder", type=int)
    args = parser.parse_args()

    numeric_level = getattr(logging, args.loglevel.upper(), None)
    form = '%(levelname)s :: %(asctime)s :: %(message)s'
    logging.basicConfig(level=numeric_level, format=form)

    with open('sismo.cat', 'rb') as sismo:
        # passe la premiere ligne
        head = unpack('iiihh', sismo.read(16))
        logging.info('numero de station geostar : %s' % head[4])

        for i in range(args.bloc):
            infos = sismo.read(16)
            time_t, point_dat, decalage, etat_trig, cor_gps, skew, tcxo = unpack('iihhhBB', infos)
            utc_dt = gmtime(time_t)
            utc_dt = strftime('%d %b %Y %H:%M:%S', utc_dt)
            logging.info("temps utc : %s " % utc_dt)
            logging.info("offset dans sismo.dat: %s" % point_dat)

            with open("sismo.dat", "rb") as fichier:

                liste_des_bloc = list_bloc(fichier)
                deconfit = decompression(fichier, point_dat)

            deconfit = map(float, deconfit)
            # Convert to NumPy character array
            data = np.ndarray((len(deconfit),), buffer=np.array(deconfit), dtype=float)

            # Fill header attributes
            stats = {'network': '70', 'station': 'GEO1', 'location': '',
                     'channel': '70Z', 'npts': len(data), 'sampling_rate': 75,
                     'mseed': {'dataquality': 'D'}}
            # set current time
            stats['starttime'] = UTCDateTime(time_t)
            st = Stream([Trace(data=data, header=stats)])
            st.plot(outfile='graphe%s.png' %i)
            

            logging.debug(st[0].stats)
            # write as INT16 file (encoding=0)
            st.write("sismo%s.mseed" %i, format='MSEED')

            # Show that it worked, convert NumPy character array back to string
        
    os.system('find *mseed* -exec cat {} \; > sismoh.mseed')

    with open('sismoh.mseed', 'rb') as sismo:
        st = read(sismo)
        st.plot(outfile='grapheh.png')

