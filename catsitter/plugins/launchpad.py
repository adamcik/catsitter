#! /usr/bin/python
# encoding: utf-8

import re
import sys
import urllib2

from email.parser import Parser
from catsitter import register

BUG_API_URL = 'https://launchpad.net/bugs/%s/+text'
BUG_URL = 'https://launchpad.net/bugs/%s'

@register('(?P<bugline>.*(LP)?#\d+.*)')
def handler(bugline=None):

    result = []

    for bug in re.findall('(?:LP)?#(\d+)', bugline):
        try:
            url = urllib2.urlopen(BUG_API_URL % bug)
        except urllib2.HTTPError, e:
            continue

        parser = Parser()
        message = parser.parse(url)

        result.append('[%s] %s (%s)' % (bug, message['title'], BUG_URL % bug))

    return result
