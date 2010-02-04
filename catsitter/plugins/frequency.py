#! /usr/bin/python

import csv
import glob
import re

from decimal import Decimal
from catsitter import decode, register, get_data_file

@register('!freq (?:(?P<frequency>\d{1,3}(?:[,.]\d*))|(?P<channel>R[VU]-?\d{1,3}))\s*')
def handler(frequency=None, channel=None):

    qrgfiles = glob.glob(get_data_file('*.qrg'))
    result = []

    if channel:
        search = channel.replace('-', '')
    elif frequency:
        search = Decimal(frequency.replace(',', '.'))
        search = '%d' % (search * 1000000)
    else:
        return

    for file in qrgfiles:
        signreader = csv.reader(open(file), delimiter=',')

        for row in signreader:
            if len(row) != 3:
                continue

            freq, mode, name = map(decode, row)

            if re.match(search, freq) or re.match(search, name.replace('-', '')):
                result.append('%.3f - %s (%s)' % (Decimal(freq) / 1000000, name, mode))

    if not result:
        return ['%s er ukjent' % (frequency or channel)]

    return result
