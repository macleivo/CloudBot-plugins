"""
distance.py

Find the total trip distance between locations.

Created by:
    - Marcus Leivo

License:
    GNU General Public License (Version 3)
"""
import json

from urllib.request import urlopen, quote
from cloudbot import hook


# API URL
api_key = "<your key here>"
api_url = 'http://open.mapquestapi.com/directions/v2/routematrix?key=' + api_key + '&unit=k&from='


@hook.command('matka', 'dist')
def dist(text):
    """
    .dist <city1> <city2> [pedestrian], or <city1>|<city2>|[pedestrian] if there is whitespace in the names.
    """

    # checks if locations are not given
    if not text:
        return("'.dist <city1> <city2>' or if there is any whitespace in a city's name then '.dist <city1>|<city2>'")

    args = ''
    # Splits the locations into args. (Los Angeles|Seattle -> ['Los Angeles', 'Seattle'])
    # if no '|' is found then uses spaces to split (Los Angeles Seattle -> ['Los', 'Angeles', 'Seattle'])
    if text.find(';') != -1:
        args = text.replace(" ; ", ";").split(';')
    else:
        args = text.split(' ')

    if len(args) > 10:
        return("Too many destinations to route!")

    # <---- STORING ---->
    # Store the locations into variables

    # Accepted formats for using walking route
    pedestrian_route = ['pedestrian', 'walk', 'walking', 'kävely', 'kävellen', 'bicycle', 'pyörä', 'pyörällä', 'apostolinkyyti']

    # Handles cases with two arguments e.g. "London Paris" or "London|Paris"
    method = "fastest"
    if args[-1].lower() in pedestrian_route:
        method = "pedestrian"
        args = args[:-1]

    # <---- ALIASES ---->
    for loc in range(len(args)):
        if args[loc].lower() == "hese": args[loc] = "helsinki"
        if args[loc].lower() == "ptown": args[loc] = "porvoo"

    # <---- LENGTHS & DURATIONS ---->
    lengths = []
    durations = []
    for loc in range(0, len(args)-1):
        start = args[loc]
        destination = args[loc+1]
        url = api_url + quote(start) + '&to=' + quote(destination) + "&routeType=" + quote(method)
        resp = json.loads(urlopen(url).read().decode())
        # Checks if given locatios are supported
        if resp['info']['statuscode'] != 0:
            error_message = resp['info']['messages'][0]
            if error_message.find('pedestrian') != -1:
                return("Exceeded pedestrian maximum gross distance for locations")
            else:
                return(error_message + " (%s, %s)" % (args[loc], args[loc+1]))
        lengths.append(resp['distance'][-1])
        durations.append(resp['time'][-1])

    # <---- OUTPUT ---->
    # Stores the data into variables and generates the output
    # Gets the distance and converts the distance into an appropriate format
    length = sum(lengths)
    if 1 > length >= 0:
        length = str(round(float(length), 2) * 1000) + "m"
    elif 10 > length >= 1:
        length = str(round(length, 1)) + "km"
    else:
        length = str(int(round(length, 0))) + "km"

    # Gets the duration (which unfortunately, is in seconds)
    duration = sum(durations)
    days = ""
    hours = ""
    minutes = ""
    # Counts how many days and stores the modulus (hours and minutes) into duration
    if duration >= 86400:
        days = int(duration / 86400)
        duration = duration % 86400
    # Counts the hours the same way days are counted
    if duration >= 3600:
        hours = int(duration / 3600)
        duration = duration % 3600
    # Counts the minutes and rounds up if there are 30 or more seconds left
    # over
    if duration >= 60:
        if duration % 60 >= 30:
            minutes = int(duration / 60) + 1
        else:
            minutes = int(duration / 60)

    # Generates the duration output
    duration = ""
    if days != "":
        duration += str(days) + "d "
    if hours != "":
        duration += str(hours) + "h "
    if minutes != "":
        duration += str(minutes) + "min "
    if duration == "":
        duration = "Less than half a minute."

    routetype = ""
    if method == "pedestrian":
        routetype = "(Walking route)"
    return('Distance: ' + length + ', Duration: ' + duration + routetype)
