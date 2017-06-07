'''
Created on 31 mag 2017

@author: Geko
'''
import telegram
from telegram.keyboardbutton import KeyboardButton

from bot.models import Preference, User, Cronology
import main

def addPreferencesKeyboard(keyboard, user):
    preferences = Preference.objects.filter(bot_user = user)
    for p in preferences:
        button = KeyboardButton(text=p.label)
        keyboard.append([button])  
        
def getSinglePreference(user, labelToAnalyze):
    preference = Preference.objects.get(bot_user=user, label=labelToAnalyze)
    return preference

def createPreference(text, user, address):
    preference = Preference()
    preference.label = text
    preference.lat = user.lat
    preference.lon = user.lon
    reverse_geocode_result = main.gmaps.reverse_geocode((user.lat, user.lon))
    preference.address = reverse_geocode_result[0]['formatted_address']
    preference.bot_user = user
    preference.save()  
    
def savePreferences(bot, update):
    yes_keyboard = KeyboardButton(text="YES")
    no_keyboard = KeyboardButton(text="NO")
    custom_keyboard = [[ yes_keyboard], [no_keyboard]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)
    user = User.objects.get(chat_id=update.message.chat_id)
    newCommand = user.lastCommand + ".choose"
    User.objects.filter(chat_id=update.message.chat_id).update(lastCommand = newCommand)
    bot.sendMessage(chat_id=update.message.chat_id, text = "Do you want to save this location for future searches?", reply_markup=reply_markup)
    
def checkPreferences(utente, text, bot, update):
    preferences = Preference.objects.filter(bot_user=utente)
    for p in preferences:
        if p.label == text:
            return True
    return False