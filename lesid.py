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
    """ return the list of bloc include in datfile """
    list_bloc = []
    while True:
        try:
            bloc_begin = datfile.tell()
            size_block, =  unpack("h", datfile.read(2))
        except struct.error:
            break
        else:
            list_bloc.append(bloc_begin)
            datfile.seek(list_bloc[-1] + size_block + 2)
    return list_bloc


def decompression(datfile, offset_bloc):
    """ return a list of decompressed bloc data """

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
        data = datfile.read(nech/8 * nbits)
        datfile.read(nbytes - 10 - nech/8 * nbits)
        # print(hexlify(data))

        if nbits != 0:
            # donnees en binaire
            data_binaire = bin(int(hexlify(data), 16))[2:].rjust(nech * nbits,'0')
            logging.debug(len(data_binaire))

            data_undelta = [data_binaire[i * nbits:(i + 1) * nbits]
                            for i in range(nech)]
            logging.debug(len(data_undelta))
            try:
                data_undelta = [int(x, 2) - offset for x in data_undelta]
            except ValueError:
                logging.debug("erreur lors de la décompression")
                data_undelta = []
            logging.debug(data_undelta)
            data_undelta.insert(0, val0)
            data_out.extend(data_undelta)

        size_block -= nbytes
    return data_out


def dump_to_mseed(data, channel, startime):
    """ dump data to format MiniSEED """
    data = map(float, data)
    # Convert to NumPy character array
    data = np.ndarray((len(data),), buffer=np.array(data), dtype=float)

    # Fill header attributes
    stats = {'network': '70', 'station': 'GEO1', 'location': '',
             'channel': '70%s' % channel, 'npts': len(data),
             'sampling_rate': 150, 'mseed': {'dataquality': 'D'}}
    # set current time
    stats['starttime'] = UTCDateTime(startime)
    st = Stream([Trace(data=data, header=stats)])
    # st.plot(outfile='graphe%s%s.png' % (channel, stats["starttime"]))

    logging.debug(st[0].stats)
    st.write("sismo%s%s.mseed" % (channel, stats["starttime"]), format='MSEED')


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="lecture de sismo.cat")

    parser.add_argument("filecat", help="fichier sismo.cat")
    parser.add_argument("filedat", help="fichier sismo.dat")
    parser.add_argument("bloc", help="nombre de minutes à décoder", type=int)

    parser.add_argument("-l", "--loglevel", help="change the logging level",
                        default="info",
                        choices=['debug', 'info', 'warning', 'error'])
    args = parser.parse_args()

    numeric_level = getattr(logging, args.loglevel.upper(), None)
    form = '%(levelname)s :: %(asctime)s :: %(message)s'
    logging.basicConfig(level=numeric_level, format=form)

    with open(args.filecat, 'rb') as sismo:
        # passe la premiere ligne
        head = unpack('iiihh', sismo.read(16))
        logging.info('numero de station geostar : %s' % head[4])
        logging.info('code cadence échantillonage : %s' % head[3])
        # logging.warning('head {!r}'.format(head))

        liste_offset = []
        for i in range(max(2, args.bloc)):
            infos = sismo.read(16)
            time_t, point_dat, decalage, etat_trig, cor_gps, skew, tcxo = unpack('iihhhBB', infos)
            utc_dt = gmtime(time_t)
            utc_dt = strftime('%d %b %Y %H:%M:%S', utc_dt)
            logging.info("temps utc : %s " % utc_dt)
            logging.info("offset dans sismo.dat: %s" % point_dat)
            logging.info("correction horloge : %s" % cor_gps)
            # logging.warning("infos : {!r} ".format((time_t, point_dat, decalage, etat_trig, cor_gps, skew, tcxo)))
            liste_offset.append((point_dat, time_t))

    with open(args.filedat, "rb") as fichier:

        liste_des_bloc = list_bloc(fichier)
        nb_channel = liste_des_bloc.index(liste_offset[1][0])

        dict_channel = {0: 'Z',
                        1: 'N',
                        2: 'E',
                        3: '-',
                        }
        for j in range(args.bloc):
            for i in range(nb_channel):

                deconfit = decompression(fichier, liste_des_bloc[j * nb_channel + i])
                if deconfit != []:
                    if i <= 3:
                        dump_to_mseed(deconfit, dict_channel[i], liste_offset[j][1])
                    else:
                        dump_to_mseed(deconfit, '**%s' % i, liste_offset[j][1])
                else:
                    logging.info(" --> pas de données pour ce bloc")

    # os.system('find *mseed* -exec cat {} \; > sismoh.mseed')

    # with open('sismoh.mseed', 'rb') as sismo:
    #     st = read(sismo)
    #     st.plot(outfile='grapheh.png')
    #     st.printGaps()
    #     st.getGaps()
