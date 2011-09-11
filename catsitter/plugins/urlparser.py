#! /usr/bin/python
# encoding: utf-8

import re
import sys
import urllib
import urllib2

from lxml.html import fromstring
from catsitter import decode, register

RE_URL = re.compile(r'(?:\b|[(])(?P<scheme>https?://)?'
                    r'(?P<host>(?:[^ #?://]+\.)+[^ #?://]+)'
                    r'(?P<path>/[^?# ]*)?'
                    r'(?P<query>\?[^# ]*)?(?:\b|[,.?!])', re.UNICODE)


def parse_url(line):
    for scheme, host, path, query in RE_URL.findall(line):
        if not scheme:
            continue

        scheme = scheme.encode('utf-8') or 'http://'
        host = host.encode('idna')
        path = path.encode('utf-8') or ''
        query = query.encode('utf-8') or ''
        yield ''.join([scheme, host, path, query])

def pretty_url(line):
    for scheme, host, path, query in RE_URL.findall(line):
        scheme = scheme or 'http://'
        host = host.decode('idna')
        path = decode(urllib.unquote(path)) or ''
        query = decode(urllib.unquote(query)) or ''
        return u''.join([scheme, host, path, query])

def normalise_url(url):
    return re.sub(r'^https?://(www\.)?', '', url.rstrip('/'))

def title_from_elements(html, *elements):
    for element in elements:
        try:
            title = html.cssselect(element)[0].text_content()
            title = title.split('\n')
            title = map(lambda l: l.strip(), title)
            return u' '.join(title).strip()
        except IndexError:
            continue
    return ''

@register('(?P<urlline>[^!].*\w+\.\w+.*)')
def handler(urlline=None):

    result = []
    blacklist = r'(twitter.com|dpaste.com)'

    for url in parse_url(urlline):
        if re.search(blacklist, url):
            continue

        try:
            page = urllib2.urlopen(url)
        except IOError:
            return

        if page.info().get('status', '200 OK') != '200 OK':
            return

        html = fromstring(page.read())
        found = ''

        try:
            found = html.cssselect('meta[property="og:title"]')[0].attrib['content']
        except IndexError:
            found = title_from_elements(html, 'title', 'h1', 'h2')

        try:
            found = found.encode('latin1').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass

        if normalise_url(url) != normalise_url(page.geturl()):
            found += u' (%s)' % pretty_url(page.geturl())

        if found:
            result.append(u'>> ' + found.strip())

    return result
