"""
s-ryhma.py

Outputs the opening and closing times of the S Group's grocery stores.

Created by:
    - Marcus Leivo

License:
    GNU General Public License (Version 3)
"""
from __future__ import unicode_literals
import json
import requests

from urllib.parse import quote
from cloudbot import hook

import datetime


# 11120: Prisma
# 12200: ABC liikennemyymälä
#   101: S-market
#   103: Sale
#   104: Alepa
chainIDs = ['11120', '12200', '101', '103', '104']


def sKauppaLaskeAika(kauppa):
    if kauppa['opening_times_today']['type'] == "24H":
        return ""
    aukeamisaika = kauppa['opening_times_today']['start_time'].split(":")
    sulkeutumisaika = kauppa['opening_times_today']['end_time'].split(":")

    now = datetime.datetime.now()
    tunnit = now.hour + now.minute/60.0

    kauppaAukeaa = int(aukeamisaika[0]) + int(aukeamisaika[1])/60.0
    kauppaSulkeutuu = int(sulkeutumisaika[0]) + int(sulkeutumisaika[1])/60.0

    output = ""
    if kauppaSulkeutuu < kauppaAukeaa:
        kauppaSulkeutuu += 24
    if tunnit < kauppaAukeaa:
        tunteja = int(kauppaAukeaa - tunnit)
        minuutteja = int(((kauppaAukeaa - tunnit) % 1) * 60)
        output += "Aukeamiseen %sh %smin" % (tunteja, minuutteja)
    if kauppaAukeaa <= tunnit <= kauppaSulkeutuu:
        if kauppaSulkeutuu - kauppaAukeaa == 24:
            return ""
        else:
            tunteja = int(kauppaSulkeutuu - tunnit)
            minuutteja = int(((kauppaSulkeutuu - tunnit) % 1) * 60)
            output += "Sulkeutumiseen %sh %smin" % (tunteja, minuutteja)
    if tunnit > kauppaSulkeutuu:
        kauppaAukeaa = 0
        count = 1

        while kauppaAukeaa <= 0 and count < 7:
            aukeamisaika = kauppa['opening_times'][count]['start_time'].split(":")
            sulkemisaika = kauppa['opening_times'][count]['end_time'].split(":")
            kauppaAukeaa += int(aukeamisaika[0]) + int(aukeamisaika[1])/60.0
            if aukeamisaika == sulkemisaika and ":".join(aukeamisaika) == "00:00":
                return "Totuus: ei aukea"
            count += 1
        if kauppaAukeaa == 0:
            return "Totuus: ei aukea"

        tunteja = int(kauppaAukeaa + (24 - tunnit))
        minuutteja = int((kauppaAukeaa % 1) * 60 + ((1 - (tunnit % 1)) * 60))
        output += "Aukeamiseen %sh %smin" % (tunteja, minuutteja)
    return output


def sKauppaAuki(kauppa):
    aukiolot = []
    for auki in kauppa['opening_times'][:3]:
        aukeaa = ""
        kiinni = ""
        if 'start_time' in auki:
            aukeaa = auki['start_time']
        if 'end_time' in auki:
            kiinni = auki['end_time']

        tyyppi = auki['type']
        output = ""

        # Appendaa paivan aukioloajan eteen
        if len(aukiolot) == 0:
            output += "Auki tänään "
        elif len(aukiolot) == 1:
            output += "huomenna "
        else:
            output += "ylihuomenna "

        if aukeaa.find(":00") != -1 and kiinni.find(":00") != -1:
            aukeaa = aukeaa[:-3]
            kiinni = kiinni[:-3]

        # Jos aukeaa 00 ja sulkeutuu 00 niin kauppa on suljettu
        if tyyppi == "CLOSED":
            output += "suljettu"
        # Jos aukeamis- ja sulkeutumisaika muotoa XX:00
        # niin poistetaan loppunollat
        else:
            if tyyppi == "24H":
                output += "24h"
            else:
                output += aukeaa + "-" + kiinni
        aukiolot.append(output)

    return ", ".join(aukiolot)


def sryhmaHaku(nick, hakuTermit):
    url = ""
    nro = 0
    args = hakuTermit.replace(", ", ",").split(",", 1)
    try:
        nro = int(args[1]) - 1
    except:
        pass
    url = "https://karttapalvelu.s-kanava.net/map/serviceapi/search.html?output=json&maxresults=10&value=%s" % (quote(args[0]))
    url += "&chain=" + ",".join(chainIDs)
    try:
        tulokset = json.loads(requests.get(url).text)['pobs']
        kauppa = tulokset[nro]
    except:
        return("Kauppaa ei löytynyt.")

    output = "%s/%s %s" % (str(nro + 1), str(len(tulokset)), kauppa['marketingName'])
    output += " (%s)" % (kauppa['streetAddress'])
    if output == "":
        output = kauppa['name']
    try:
        output += "; " + sKauppaAuki(kauppa)
        output += "; " + sKauppaLaskeAika(kauppa)
        if output[-2:] == "; ":
            output = output[:-2]
    except:
        output += "; Aukioloaikoja: ei ole"
    return(output)


def sryhma_output(nick, ketju, kauppa):
    return sryhmaHaku(nick, ketju + " " + kauppa)


@hook.command('sryhma', 'sryhmä', 'sryhma')
def sryhma_general(text, nick):
    return sryhma_output(nick, "", text)


@hook.command('alepa')
def sryhma_alepa(text, nick):
    return sryhma_output(nick, "alepa", text)


@hook.command('sale')
def sryhma_sale(text, nick):
    return sryhma_output(nick, "sale", text)


@hook.command('smarket')
def sryhma_smarket(text, nick):
    return sryhma_output(nick, "smarket", text)


@hook.command('prisma')
def sryhma_prisma(text, nick):
    return sryhma_output(nick, "prisma", text)
