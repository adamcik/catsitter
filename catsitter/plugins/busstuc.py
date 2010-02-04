#!  /usr/bin/python

import re

from lxml.html import parse
from catsitter import register

@register('!busstuc (?P<query>.+)')
def handler(query=None):

    html = parse('http://www.idi.ntnu.no/~tagore/cgi-bin/busstuc/busq.cgi'
                 '?lang=nor&quest=' + query)

    body = html.getroot().cssselect('body')[0]

    for br in body.cssselect('br'):
        br.text = '\n'

    answer = body.text_content()
    answer = re.sub('\s+', ' ', answer)
    answer = answer.strip()
    answer = answer.replace(' . ', '. ')
    answer = answer.replace(' , ', ', ')

    return [answer]
