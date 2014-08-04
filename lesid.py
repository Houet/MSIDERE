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


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="lecture de sismo.cat")

    parser.add_argument("-l", "--loglevel", help="change the logging level",
                        default="info",
                        choices=['debug', 'info', 'warning', 'error'])
    args = parser.parse_args()

    numeric_level = getattr(logging, args.loglevel.upper(), None)
    form = '%(levelname)s :: %(asctime)s :: %(message)s'
    logging.basicConfig(level=numeric_level, format=form)

    with open('sismo.cat', 'rb') as sismo:
        # passe la premiere ligne
        sismo.read(16)
        for i in range(10):
            infos = sismo.read(16)
            time_t, point_dat, decalage, etat_trig, cor_gps, skew, tcxo = unpack('iihhhBB', infos)
            logging.info("seconde unix : %s" % time_t)
            utc_dt = gmtime(time_t)
            utc_dt = strftime('%d %b %Y %H:%M:%S', utc_dt)
            logging.info("temps utc : %s " % utc_dt)
            logging.info("offset dans sismo.dat: %s" % point_dat)
