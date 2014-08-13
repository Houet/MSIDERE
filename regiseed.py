#!/usr/bin/env python
# -*- coding=utf-8 -*-

import struct
from struct import pack, unpack


def list_bloc(datfile):
    """ return the list of bloc's offset include in datfile """
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


def list_paquet(datfile, offset_bloc):
	""" return the list of paquet's offset include in the bloc """
	list_paquet = []
	datfile.seek(offset_bloc)
	size_block, =  unpack("h", datfile.read(2))
	while size_block != 0:
		paquet_begin = datfile.tell()
		size_paquet, =  unpack("h", datfile.read(2))
		list_paquet.append(paquet_begin)
		datfile.seek(list_paquet[-1] + size_paquet)
		size_block -= size_paquet
	return list_paquet


def readpaquet(datfile, offset_paquet):
	""" return paquet data and metadata """
	datfile.seek(offset_paquet)
	header = unpack("5h", datfile.read(10))
	data = datfile.read(header[0] - 10)
	return header, data


