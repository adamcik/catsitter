import urllib
import re
import json

from catsitter import register, decode

TWITTER_URL = 'http://api.twitter.com/1/statuses/show.json?id=%s'

@register('(?P<twitterline>.*twitter\.com/(?:#!/)?\w+/status/(?:\d+).*)')
def handler(twitterline=None):
    result = []

    for status_id in re.findall('twitter\.com/(?:#!/)?\w+/status/(\d+)', twitterline):
        try:
            data = urllib.urlopen(TWITTER_URL % status_id).read()
        except IOError, e:
            continue

        if not data:
            continue

        data = json.loads(data)
        result.append(u'>> %s: %s' % (data['user']['name'], data['text']))

    return result

