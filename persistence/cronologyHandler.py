'''
Created on 31 mag 2017

@author: Geko
'''

import datetime

from bot.models import User, Cronology, Preference


def createCronology(bot, update, user):
    print(user)
    cronology = Cronology()
    cronology.bot_user = user
    cronology.command = user.lastCommand
    cronology.date = datetime.datetime.now()
    cronology.save()