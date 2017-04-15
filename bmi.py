"""
bmi.py

Calculates your bmi.

Created by:
    - Marcus Leivo

License:
    GNU General Public License (Version 3)
"""

from cloudbot import hook


@hook.command('bmi')
def bmi(text):
    args = text.split(" ")
    #Makes sure that both weight and height are given
    if len(args) < 2:
        return ".bmi <weight> <height>"

    #Saves the first given argument as weight and the second argument as height
    #Converts the decimal pointer into a dot if needed
    weight = str(args[0]).replace(',', '.')
    #Converts the decimal pointer into a dot if needed
    height = str(args[1]).replace(',', '.')

    #Makes sure that there are only digits (and an decimal pointer)
    #in the given weight
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']
    for i in range(len(weight)):
        if str(weight[i]) not in numbers:
            return(".bmi <weight> <height>")

    #Makes sure that there are only digits (and an decimal pointer)
    #in the given height
    for i in range(len(height)):
        if str(height[i]) not in numbers:
            return(".bmi <weight> <height>")

    #Calculates the bmi and responds accordingly
    else:
        #If the given height is over 3 (metres), the user has presumably
        #given the height in centimetres rather than in metres. This
        #converts the height from centimetres into metres.
        if float(height) > 3:
            height = float(float(height) / 100)

        #Calculates the body mass index
        bodymassindex = float(weight) / float(height) ** 2

        #Calculates how much the user has to lose weight
        #in order to be considered as normal weight.
        to_lose = round(float(weight) - float(height) ** 2 * 25, 22)
        to_gain = round(float(height) ** 2 * 18.5 - float(weight), 2)

        #Compares the user's bmi into this chart
        #https://en.wikipedia.org/wiki/Body_mass_index#Categories
        bmi_rounded = int(bodymassindex) + round(bodymassindex % 1, 2)
        if bodymassindex < 15.0:
            return("Your BMI is %s, very severely underweight. You have to gain %skg for normal bmi." % (bmi_rounded, to_gain))
        elif 15.0 <= bodymassindex < 16.0:
            return("Your BMI is %s, severely underweight. You have to gain %skg for normal bmi." % (bmi_rounded, to_gain))
        elif 16.0 <= bodymassindex < 18.5:
            return("Your BMI is %s, underweight. You have to gain %skg for normal bmi." % (bmi_rounded, to_gain))
        elif 18.5 <= bodymassindex < 25.0:
            return("Your BMI is %s, healthy weight." % (bmi_rounded))
        elif 25.0 <= bodymassindex < 30.0:
            return("Your BMI is %s, overweight. You have to lose %skg for normal bmi." % (bmi_rounded, to_lose))
        elif 30.0 <= bodymassindex < 35.0:
            return("Your BMI is %s, moderately obese. You have to lose %skg for normal bmi." % (bmi_rounded, to_lose))
        elif 35.0 <= bodymassindex < 40.0:
            return("Your BMI is %s, severely obese. You have to lose %skg for normal bmi." % (bmi_rounded, to_lose))
        else:
            return("Your BMI is %s, very severely obese. You have to lose %skg for normal bmi." % (bmi_rounded, to_lose))
