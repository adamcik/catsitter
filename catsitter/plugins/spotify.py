#! /usr/bin/python

import urllib
import re

from lxml.objectify import fromstring
from catsitter import register, decode

SPOTIFY_URL = 'http://ws.spotify.com/lookup/1/?uri=spotify:%s:%s'

@register('(?P<spotifyline>.*spotify:(track|artist|album):[A-Za-z0-9]+.*)')
def handler(spotifyline=None):
    result = []

    for type, id in re.findall('spotify:(track|artist|album):([A-Za-z0-9]+)', spotifyline):
        try:
            xml = urllib.urlopen(SPOTIFY_URL % (type, id)).read()
        except IOError, e:
            continue

        if not xml:
            continue

        data  = fromstring(xml)

        if type == 'artist':
            result.append(u'>> %s' % data.name)
        else:
            artists = [unicode(artist.name) for artist in data.artist]

            if len(artists) > 4:
                artists = u', '.join(artists[:4]) + u', ...'
            elif len(artists) > 1:
                artists = u', '.join(artists[:-1]) + u' and ' + artists[-1]
            else:
                artists = artists[0]

            result.append(u'>> %s by %s' % (data.name, artists))

    return result
