#! /usr/bin/python

import csv
import re

from catsitter import register, decode, get_data_file

@register('!call (?P<callsign>\w+.*)')
def handler(callsign=None):

    signfile = get_data_file('callsigns.csv')
    signreader = csv.reader(open(signfile), delimiter=';')

    result = []

    for row in signreader:
        call, name, addr, code, place = map(decode, row[:5])

        if call == callsign:
            result.append('%-7s %s (%s)' % (call, name, place))
        elif re.search(callsign, name, re.I):
            result.append('%-7s %s (%s)' % (call, name, place))

    if not result:
        return ['%s er ukjent' % callsign]
    elif len(result) > 5:
        return result[:5] + ['og %d til...' % (len(result) - 5)]

    return result
