"""
ask.py

Ask CloudBot something! You can ask multiple questions by separating questions
with "&&". You can also ask CloudBot to choose from a list of items by
separating items with "or".

Created by:
    - Marcus Leivo

License:
    GNU General Public License (Version 3)
"""
from cloudbot import hook
from random import choice


@hook.command('ask', 'kysy')
def rand(text):
    vastaukset = ['y', 'n']

    if not text:
        return "Are you going to ask me something?"

    if text.find(' or ') != -1 and text.find(' && ') != -1:
        output = ""
        for i in text.split(' && '):
            choice_list = []
            if i.find(' or ') != -1:
                choice_list = i.split(' or ')
                output += choice(choice_list) + " of course and "
            else:
                output += choice(vastaukset) + " and "
        return output[:-4]

    elif text.find(' or ') != -1:
        choice_list = text.split(' or ')
        return choice(choice_list) + " of course!"

    elif text.find(' && ') != -1:
        choice_list = text.split(' && ')
        output = ""
        for i in choice_list:
            output += choice(vastaukset) + " and "
        return output[:-4]

    else:
        return choice(vastaukset)
