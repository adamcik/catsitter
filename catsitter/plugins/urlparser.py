#! /usr/bin/python
# encoding: utf-8

import re
import sys
import urllib2

from lxml.html import fromstring
from catsitter import decode, register

RE_URL = re.compile(r'\b(?P<scheme>[a-z+]+://)?'
                    r'(?P<host>(?:[^ ]+\.)+\w+)'
                    r'(?P<port>:[0-9]*)?'
                    r'(?P<path>/[^?#]*)?'
                    r'(?P<query>\?[^#]*)?\b')

@register('(?P<urlline>[^!].*\w+\.\w+.*)')
def handler(urlline=None):

    result = []

    for m in RE_URL.findall(urlline):
        if not m:
            continue

        scheme, host, port, path, query = m

        if scheme and not re.match('https?://', scheme):
            continue

        url = ''.join([scheme or 'http://',
                       host,
                       port or '',
                       path or '',
                       query or ''])
        try:
            page = urllib2.urlopen(url)
        except IOError:
            return

        if page.info().get('status', '200 OK') != '200 OK':
            return

        htmlstring = decode(page.read())

        html = fromstring(htmlstring)
        found = ''

        for element in ['title', 'h1', 'h2']:
            try:
                title = html.cssselect(element)[0].text_content()
                title = title.split('\n')
                title = map(lambda l: l.strip(), title)

                title = u'«%s»' % u' '.join(title).strip()

                found = title
                break
            except IndexError:
                continue

        if url != page.geturl():
            found += ' (%s)' % page.geturl()

        if found:
            result.append(found.strip())

    if result:
        return [' - '.join(result)]
