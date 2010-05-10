#! /usr/bin/python
# encoding: utf-8

import re
import sys
import urllib
import urllib2

from lxml.html import fromstring
from catsitter import decode, register

RE_URL = re.compile(r'(?:\b|[(])(?P<scheme>[a-z+]+://)?'
                    r'(?P<hostpath>(?:[^ ]+\.)+[^/]+(?:/[^?#]*)?)'
                    r'(?P<query>\?[^#]*)?(?:\b|[,.?!])', re.UNICODE)


def parse_url(line):
    for scheme, hostpath, query in RE_URL.findall(line):
        if scheme and not re.match('https?://', scheme):
            continue

        try:
            host, path = hostpath.split('/', 1)
        except ValueError:
            host, path = hostpath, ''
        scheme = scheme.encode('utf-8') or 'http://'
        host = host.encode('idna')
        path = path.encode('utf-8') or ''
        query = query.encode('utf-8') or ''
        yield ''.join([scheme, host, '/', path, query])

def pretty_url(line):
    for scheme, hostpath, query in RE_URL.findall(line):
        try:
            host, path = hostpath.split('/', 1)
        except ValueError:
            host, path = hostpath, ''
        scheme = scheme or 'http://'
        host = host.decode('idna')
        path = decode(urllib.unquote(path)) or ''
        query = decode(urllib.unquote(query)) or ''
        return u''.join([scheme, host, u'/', path, query])

@register('(?P<urlline>[^!].*\w+\.\w+.*)')
def handler(urlline=None):

    result = []

    for url in parse_url(urlline):
        try:
            page = urllib2.urlopen(url)
        except IOError:
            return

        if page.info().get('status', '200 OK') != '200 OK':
            return

        html = fromstring(page.read())
        found = ''

        for element in ['title', 'h1', 'h2']:
            try:
                title = html.cssselect(element)[0].text_content()
                title = title.split('\n')
                title = map(lambda l: l.strip(), title)
                found = u' '.join(title).strip()
                break
            except IndexError:
                continue

        try:
            found = found.encode('latin1').decode('utf-8')
        except UnicodeDecodeError:
            pass

        if url != page.geturl():
            found += u' (%s)' % pretty_url(page.geturl())

        if found:
            result.append(u'>> ' + found.strip())

    return result
