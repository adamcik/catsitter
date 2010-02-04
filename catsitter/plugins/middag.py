#! /usr/bin/python

import re
import urllib
import vobject

from datetime import date
from lxml.html import fromstring
from catsitter import register, decode

def samfundet():
    try:
        page= urllib.urlopen('http://www.samfundet.no/arrangement/ical_kategori/lyche')
    except IOError, e:
        return 'Samfundet: ' + str(e)

    today = date.today()

    try:
        ical = vobject.readOne(page.read())
    except vobject.base.VObjectError, e:
        print >> sys.stderr, icalstring
        return 'Samfundet: ' + str(e)

    for child in ical.getChildren():
        if child.name != 'VEVENT':
            continue

        start = child.dtstart.value.date()
        if start != today:
            continue

        location = child.location.value
        summary = child.summary.value.lstrip('Middag: ')

        return ' - '.join([location, summary])

    return 'Samfundet: Could not find dinner'

def sit(item, name):
    try:
        htmlstring = urllib.urlopen('http://www.sit.no/content.ap?thisId=%s' % item).read()
        root = fromstring(decode(htmlstring))
    except IOError, e:
        return '%s: %s' % (name, e)

    days = ['Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag', '', '']
    today = days[date.today().weekday()]
    menu = root.cssselect('#menytable')[0]
    meals = []

    for tr in menu.cssselect('tr'):
        day = tr.cssselect('td.ukedag')

        if day and day[0].text_content().strip() != today:
            continue

        for innertr in tr.cssselect('td.dagsmenyContainer tr'):
            meal = innertr.cssselect('td.menycelle')
            price = innertr.cssselect('td.priscelle')

            if not meal or not price:
                continue

            meal = meal[0].text_content().strip()
            price = price[0].text_content().strip()

            if meal and price:
                meals.append('%s (%s)' % (meal, price))

    if not meals:
        return u'%s - Nothing found' % name

    return name + ' - ' + '; '.join(meals)

@register('!middag\s*')
def handler():

    result = []
    result.append(samfundet())
    result.append(sit(36444, 'Hangaren'))
    result.append(sit(36447, 'Realfag'))

    return result
