'''
Created on 02 giu 2017

@author: Geko
'''

from bot.models import User, Cronology, Preference

def getUser(chatId):
    user = User.objects.get(chat_id=chatId)
    return user

def getUserBotActived(chatId):
    user = User.objects.get(chat_id=chatId)
    return user.botActived

def setUserLastCommand(chatId, command):
    User.objects.filter(chat_id=chatId).update(lastCommand = command)
    
def setUserLatLong(chatId, latid, long):
    User.objects.filter(chat_id=chatId).update(lat=latid, lon=long)
    
def setUserPositionName(chatId, position):
    User.objects.filter(chat_id=chatId).update(positionName=position)
    
def setUserBotActived(chatId, value):
    User.objects.filter(chat_id=chatId).update(botActived=value)