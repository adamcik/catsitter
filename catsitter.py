#! /usr/bin/python

import socket
import sys
import re
import urllib2

import catsitter

from optparse import OptionParser

socket.setdefaulttimeout(25)

opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'catsitter')]
urllib2.install_opener(opener)

def optparse():
    parser = OptionParser()
    parser.add_option('--config', action='store_true', default=False)
    parser.add_option('--settings')
    return parser

def decode(string):
    if isinstance(string, unicode) or string is None:
        return string

    try:
        string = string.decode('utf-8')
    except UnicodeDecodeError:
        string = string.decode('iso-8859-1')
    return string

def config():
    results = []

    for regexp, handler in catsitter.registry:
        results.append(regexp)

    print 'match = ^($nick: ?)?(%s)$' % '|'.join(results)

def dispatch(nick, target, source, message):
    results = []

    for regexp, func in catsitter.registry:
        match = re.search('^($nick: ?)?(%s)$' % regexp, message)

        if not match:
            continue

        result = func(**match.groupdict()) or []
        result = filter(lambda r: r is not None, result)

        results.extend(result)

    for line in results:
        print line.encode('utf-8')

def main():
    parser = optparse()
    (options, args) = parser.parse_args()

    if not options.settings:
        parser.error('no settings set')

    __import__('catsitter.settings.%s' % options.settings)

    if options.config:
        config()
    elif len(args) == 4:
        dispatch(*args)
    else:
        parser.print_usage()

if __name__ == '__main__':
    sys.exit(main())
