"""
fmi.py

Outputs the current weather conditions using Finnish Meteorological Institute's
api. Supports only locations in Finland.

Created by:
    - Marcus Leivo

License:
    GNU General Public License (Version 3)
"""
from urllib.parse import quote
from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime

import xml.etree.ElementTree as ET

from sqlalchemy import Table, Column, PrimaryKeyConstraint, String
from cloudbot import hook
from cloudbot.util import timeformat, web, database

api_key = "<your api key here>"
api_url = "http://data.fmi.fi/fmi-apikey/" + api_key + "/wfs?request=getFeature&storedquery_id=fmi::observations::weather::multipointcoverage&parameters=t2m,rh,td,wd_10min,ws_10min,wg_10min,r_1h,pressure,snow_aws,n_man,vis&place="


table = Table(
    "fmi",
    database.metadata,
    Column('nick', String(25)),
    Column('loc', String(35)),
    PrimaryKeyConstraint('nick')
)


@hook.on_start()
def load_cache(db):
    """
    :type db: sqlalchemy.orm.Session
    """
    global fmi_cache
    fmi_cache = []
    for row in db.execute(table.select()):
        nick = row["nick"]
        location = row["loc"]
        fmi_cache.append((nick, location))


def getUserFmiLocation(nick, locality):
    if not locality:
        fmi_loc = [row[1] for row in fmi_cache if nick.lower() == row[0]]
        if not fmi_loc:
            return None
        else:
            locality = fmi_loc[0]
    else:
        locality = locality

    # Aliases
    if locality.lower() == "hese":
        locality = "helsinki"
    if locality.lower() == "ptown":
        locality = "porvoo"

    return locality.lower()


def fmiTestIfNone(x):
    if x:
        return x
    return ""


def fmiWindDir(degs):
    if 22.5 < degs <= 67.5:
        return "Koillistuulta"
    if 67.5 < degs <= 112.5:
        return "Itätuulta"
    if 112.5 < degs <= 157.5:
        return "Kaakkoistuulta"
    if 157.5 < degs <= 202.5:
        return "Etelätuulta"
    if 202.5 < degs <= 247.5:
        return "Lounaistuulta"
    if 247.5 < degs <= 292.5:
        return "Länsituulta"
    if 292.5 < degs <= 337.5:
        return "Luoteistuulta"
    return "Pohjoistuulta"


def genFmiOutput(station, time, info):
    output = "%s (%s) - " % (station, time)

    while len(info) < 11:
        info.append("NaN")
    # TODO: use something other than duct tape here
    observations = {"0Lämpötila": (info[0], "°C"),
                    "1Kosteus": (info[1], "%"),
                    "2Kastepiste": (info[2], "°C"),
                    "3windDirection": (info[3], ""),
                    "4windSpeed": (info[4], "m/s"),
                    "5Puuska": (info[5], "m/s"),
                    "6Tunnin sadekertymä": (info[6], "mm"),
                    "7Paine": (info[7], "hPa"),
                    "8Lumensyvyys": (info[8], "cm"),
                    "9Pilvisyys": (info[9], ""),
                    "xNäkyvyys": (info[10], "km")}
    if observations["1Kosteus"][0] != "NaN":
        observations["1Kosteus"] = (str(int(round(float(observations["1Kosteus"][0])))), observations["1Kosteus"][1])

    for i in sorted(observations.keys()):
        if observations[i][0] == "NaN" or len(observations[i][0]) <= 0:
            observations.pop(i)
        else:
            if i[0] in ["0", "1", "2", "5", "6", "7", "8"]:
                output += "%s %s %s; " % (i[1:], observations[i][0], observations[i][1])
            if i[0] == "3":
                output += fmiWindDir(float(observations[i][0]))
            if i[0] == "4":
                output += " %s %s; " % (observations[i][0], observations[i][1])
            if i[0] == "9":
                output += "%s %s/8; " % (i[1:], str(int(float(observations[i][0]))))
            if i[0] == "x":
                output += "%s %s %s; " % (i[1:], int(round(float(observations[i][0])/1000)), observations[i][1])
    time = " (%s)" % (time)

    return output.replace(".", ",")

@hook.command("saa", "sää")
def saa(text, nick):
    locality = getUserFmiLocation(nick, text)
    if not locality:
        return "Hnnngh annas ny locality tai sit aseta default location komennolla .setlocation <locality>"
    haku = "http://ilmatieteenlaitos.fi/saa-ja-meri?p_p_id=locationmenuportlet_WAR_fmiwwwweatherportlets&p_p_lifecycle=2&p_p_mode=view&doAsUserLanguageId=fi_FI&term=" + quote(locality.lower())
    tulokset = (urlopen(haku).read().decode())[8:].split('",')[0]
    if "vantaa" in tulokset.lower() or "vantaa" == tulokset.lower():
        tulokset = "Helsinki-Vantaan lentoasema, Vantaa"
        global api_url
        api_url =  api_url[:-6]
        locality = "fmisid=100968"
    url = "http://ilmatieteenlaitos.fi/saa/" + quote(tulokset)
    soup = BeautifulSoup(urlopen(url).read().decode())

    locality = locality.replace(" ", "")
    tulokset = tulokset.replace(" ", "")

    xml_api = api_url + quote(locality)
    if "fmisid=100968" == locality:
        xml_api = api_url + locality

    root = None
    try:
        tree = ET.parse(urlopen(xml_api))
        root = tree.getroot()
    except:
        pass

    if not root:
        xml_api = api_url + quote(tulokset)
    try:
        tree = ET.parse(urlopen(xml_api))
        root = tree.getroot()
    except:
        return "Osta uus paikkakunta"


    # Päivän pituus, sekä auringonnousu ja -lasku
    try:
        paivan_pituus = soup.find_all("div", attrs={"class": "celestial-status-text"})[1].text.replace(". ", "; ", 2)[1:]
    except:
        paivan_pituus = ""

    try:
        info = root[0][0][6][0][1][0][1].text.splitlines()[-2].strip().split(" ")
    except:
        return "Paikkakuntaas ei tueta."
    station = root[0][0][5][0][1][0][0][0][0].text
    time = datetime.fromtimestamp(int(root[0][0][6][0][0][0][0].text.splitlines()[-2].strip().split(" ")[-1])).strftime('%H:%M')

    return genFmiOutput(station, time, info) + paivan_pituus


@hook.command()
def setlocation(text, nick, db):
    paikkakunta = text
    if not paikkakunta:
        return "Tarvin vielä jonku paikkakunnanki."

    haku = "http://ilmatieteenlaitos.fi/saa-ja-meri?p_p_id=locationmenuportlet_WAR_fmiwwwweatherportlets&p_p_lifecycle=2&p_p_mode=view&doAsUserLanguageId=fi_FI&term=" + quote(paikkakunta.lower())
    tulokset = (urlopen(haku).read().decode())[8:].split('",')[0]
    if len(tulokset)<3:
        bot.say("Paskat paikkakunnat sul :D")
        return
    else:
        paikkakunta = str(tulokset)
        if paikkakunta.find(",") != -1:
            maaJaCity = paikkakunta.split(", ")
            maa = maaJaCity[1]
            city = maaJaCity[0]
            paikkakunta = city

    db.execute("insert or replace into fmi(nick, loc) values (:nick, :location)",
               {'nick': nick.lower(), 'location': paikkakunta})
    db.commit()
    load_cache(db)
    return "Paikkakunta on nyt " + paikkakunta
