'''
Created on 24 mar 2017

@author: Geko - Rocco
'''

from builtins import str
import json
import logging
import os
import sys
import urllib

import django
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import googlemaps
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram.keyboardbutton import KeyboardButton
import builtins
import aimlHandler


TOKEN = "343706215:AAEaTYl_qXHsPxKMwC5rXRnrnESKEuThT2Y"
gmaps = googlemaps.Client(key='AIzaSyCHw4CGzrZOpOleKM3KCPPMI7jJV_MDkDI')
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
#WEBAPP = "145.94.189.32:8000/accounts/login"
#WEBAPP = "127.0.0.1:8000/accounts/login"
#WEBAPP = "145.94.190.106:8000/accounts/login"
WEBAPP = "192.168.178.12:8000/accounts/login"
choosenPosition = ''
lastUpdate = ""
#builtins.botActived =True

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
kernel = aimlHandler.initializeBot()


def start(bot, update, args, chat_data):
    name = update.message.from_user["first_name"]
    surname = update.message.from_user["last_name"]
    utente = User()
    utente.name = name
    utente.surname = surname
    utente.lastCommand = "start"
    utente.chat_id = update.message.chat_id
    utente.save()
    settings.USER = utente.chat_id
    cronologyHandler.createCronology(bot, update, utente)
    parking_keyboard = KeyboardButton(text="Can you find me a parking?")
    chargePoint_keyboard = KeyboardButton(text="Can you find me a electric charge point?")
    custom_keyboard = [[ parking_keyboard],[chargePoint_keyboard]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)
    print("__________CHAT_ID__________")
    print(utente)
    global lastUpdate 
    lastUpdate= str(update.update_id)
    update.message.reply_text('Hi ' + name + ' ' + surname + ', I\'m Smartbot!')
    bot.sendMessage(chat_id = update.message.chat_id, text="How can i help you?", reply_markup=reply_markup)

def talk(bot, update):
    global kernel
    botActived = userHandler.getUserBotActived(update.message.chat_id)
    if botActived:
        bot.sendMessage(chat_id=update.message.chat_id, text = kernel.respond(update.message.text))
        if 'Yes i was created to search parkings in Amsterdam' in kernel.respond(update.message.text): 
            userHandler.setUserBotActived(update.message.chat_id, False)
            print("BOT ACTIVED - parking")
            parkingHandler.parking(bot, update)
        elif 'Yes i was created to search electric charge points in Amsterdam' in kernel.respond(update.message.text): 
            userHandler.setUserBotActived(update.message.chat_id, False)
            print("BOT ACTIVED - chargePoint")
            electricChargePointHandler.chargePoint(bot, update)
    else:
        analyzeText(bot, update)
    
def profile(bot, update, args, chat_data):
    user = userHandler.getUser(update.message.chat_id)
    userHandler.setUserLastCommand(update.message.chat_id, "webappUser")
    cronologyHandler.createCronology(bot, update, user)
    bot.sendMessage(chat_id=update.message.chat_id, 
                    text='<a href="' + WEBAPP + '?chatId=' + str(update.message.chat_id) + '">User Cronology</a>', 
                    parse_mode=telegram.ParseMode.HTML)
      
def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))

def getLocation(bot, update):
    latid = update.message.location["latitude"]
    long = update.message.location["longitude"]
    userHandler.setUserLatLong(update.message.chat_id, latid, long)
    reverse_geocode_result = gmaps.reverse_geocode((latid, long))
    name = update.message.from_user["first_name"]
    message = name + " you are located in: " + reverse_geocode_result[0]['formatted_address']
    bot.sendMessage(chat_id=update.message.chat_id, 
                        text = message)
    utente = userHandler.getUser(update.message.chat_id)
    if utente.lastCommand == "parking":
        parkingHandler.location(bot, update)
    elif utente.lastCommand == "chargePoint":
        electricChargePointHandler.location(bot, update)
    
def analyzeText(bot, update):
    utente = userHandler.getUser(update.message.chat_id)
    address = ''
    print(update.message.text)
    if utente.lastCommand == 'start':
        textToAnalyze = update.message.text
        if textToAnalyze=='Find me the closest Parking':
            parkingHandler.parking(bot, update)
            print("STATO START - textToAnalyze")
    elif utente.lastCommand == "parking":
        textToAnalyze = update.message.text
        if preferenceHandler.checkPreferences(utente, textToAnalyze, bot, update):
            preference = preferenceHandler.getSinglePreference(utente, textToAnalyze)
            userHandler.setUserLatLong(update.message.chat_id, preference.lat, preference.lon)
            parkingHandler.location(bot, update)
        else:
            bot.sendMessage(chat_id=update.message.chat_id, text = "Please insert the location you want to start")
            choosenPosition = update.message.text
            print('Posizione scelta: ' + choosenPosition)
            newCommand = utente.lastCommand + ".preference"
            userHandler.setUserLastCommand(update.message.chat_id, newCommand)
    elif utente.lastCommand == "chargePoint":
        textToAnalyze = update.message.text
        if preferenceHandler.checkPreferences(utente, textToAnalyze, bot, update):
            preference = preferenceHandler.getSinglePreference(utente, textToAnalyze)
            userHandler.setUserLatLong(update.message.chat_id, preference.lat, preference.lon)
            electricChargePointHandler.location(bot, update)
        else:
            bot.sendMessage(chat_id=update.message.chat_id, text = "Please insert the location you want to start")
            choosenPosition = update.message.text
            newCommand = utente.lastCommand + ".preference"
            userHandler.setUserLastCommand(update.message.chat_id, newCommand)
    elif utente.lastCommand == "parking.preference":
            textToAnalyze = update.message.text
            geocode_result = gmaps.geocode(textToAnalyze)
            if geocode_result:
                userHandler.setUserPositionName(update.message.chat_id, textToAnalyze)
                preferenceHandler.savePreferences(bot, update)
            else:
                message = "I couldn't find this location. \nType again"
                bot.sendMessage(chat_id=update.message.chat_id, text = message )
    elif utente.lastCommand == "chargePoint.preference":
            textToAnalyze = update.message.text
            geocode_result = gmaps.geocode(textToAnalyze)
            if geocode_result:
                userHandler.setUserPositionName(update.message.chat_id, textToAnalyze)
                preferenceHandler.savePreferences(bot, update)
            else:
                message = "I couldn't find this location. \nType again"
                bot.sendMessage(chat_id=update.message.chat_id, text = message )
    elif utente.lastCommand == "parking.result":
        print("sono nel parking.result")
        #print(utente.lastCommand)
        user = userHandler.getUser(update.message.chat_id)
        parkingHandler.parkingResult(bot, update)
        print(geocode_result)
    elif utente.lastCommand == "chargePoint.result":
        print("sono nel chargePoint.result")
        #print(utente.lastCommand)
        user = userHandler.getUser(update.message.chat_id)
        electricChargePointHandler.chargePointResult(bot, update)
        print(geocode_result)
#UNIFORMATO      
    elif (utente.lastCommand == "parking.preference.choose") or (utente.lastCommand == "chargePoint.preference.choose"):
        textToAnalyze = update.message.text
        user = userHandler.getUser(update.message.chat_id)        
        geocode_result = gmaps.geocode(user.positionName)
        if geocode_result:
            address = geocode_result[0]['formatted_address']
            message = "You inserted this location " + address
            latid = geocode_result[0]['geometry']['location']['lat']
            long = geocode_result[0]['geometry']['location']['lng']
            userHandler.setUserLatLong(update.message.chat_id, latid, long)
            if textToAnalyze == "YES":
                bot.sendMessage(chat_id=update.message.chat_id, text = "Choose the name you want to save this position: " )
                newCommand = utente.lastCommand + ".save"
                userHandler.setUserLastCommand(update.message.chat_id, newCommand)
            elif textToAnalyze == "NO":
                if "parking" in utente.lastCommand :
                    newCommand = "parking.result"
                    userHandler.setUserLastCommand(update.message.chat_id, newCommand)
                    user = userHandler.getUser(update.message.chat_id)
                    parkingHandler.parkingResult(bot, update)
                elif "chargePoint" in utente.lastCommand :
                    newCommand = "chargePoint.result"
                    userHandler.setUserLastCommand(update.message.chat_id, newCommand)
                    user = userHandler.getUser(update.message.chat_id)
                    electricChargePointHandler.chargePointResult(bot, update)
                    
        else:
            message = "I couldn't find this location. \nType again"
            bot.sendMessage(chat_id=update.message.chat_id, text = message )
            #bot.sendMessage(chat_id=update.message.chat_id, text = "Type /parking if you want to start another search." )
    elif (utente.lastCommand == "parking.preference.choose.save") or (utente.lastCommand == "chargePoint.preference.choose.save"):
        textToAnalyze = update.message.text
        bot.sendMessage(chat_id=update.message.chat_id, text = "The current position has been saved with the name: " + textToAnalyze)
        user = userHandler.getUser(update.message.chat_id)
        print('ADDRESS: ' + address)
        
        if "parking" in utente.lastCommand :
            newCommand = "parking.result"
            userHandler.setUserLastCommand(update.message.chat_id, newCommand)
            preferenceHandler.createPreference(textToAnalyze, user, address)
            parkingHandler.parkingResult(bot, update)
        elif "chargePoint" in utente.lastCommand :
            newCommand = "chargePoint.result"
            userHandler.setUserLastCommand(update.message.chat_id, newCommand)
            preferenceHandler.createPreference(textToAnalyze, user, address)
            electricChargePointHandler.chargePointResult(bot, update)        
#   elif utente.lastCommand == "parking.afterDetails":
#         textToAnalyze = update.message.text
#         if textToAnalyze == "Find another parking":
#             parkingHandler.parking(bot, update)    
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text = "I couldn't understand you" )
    

        

    
def run():
    updater = Updater(TOKEN)
    choosenPosition = 'posizione'
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("parking", parkingHandler.parking))
    dp.add_handler(CommandHandler("chargePoint", electricChargePointHandler.chargePoint))
    dp.add_handler(CommandHandler("talk", talk))
    dp.add_handler(CommandHandler("profile", profile, pass_args=True, pass_chat_data=True))
    dp.add_handler(MessageHandler([Filters.location], getLocation))
    dp.add_handler(MessageHandler([Filters.text], talk))
    #dp.add_handler(MessageHandler([Filters.text], analyzeText))
    dp.add_handler(CallbackQueryHandler(get_inlineKeyboardButton, pass_chat_data=True))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()
    
    
def get_inlineKeyboardButton(bot, update, chat_data):
    query = update.callback_query
    chat_id = update['callback_query']['message']['chat']['id']
    print("chat id:" + str(chat_id))
    utente = userHandler.getUser(chat_id)
    if "parking" in utente.lastCommand:
        parkingHandler.sendMessageForSingleParking(bot, query, query.data)
    elif "chargePoint" in utente.lastCommand:
        electricChargePointHandler.sendMessageForSingleChargePoint(bot, query, query.data)

def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


if __name__ == '__main__':
    sys.path.append("C:\\Users\\Geko\\workspace\\smartBot\\smartBot") #Set it to the root of your project
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartBot.settings')
    django.setup() 
    from bot.models import User, Preference, Cronology
    from dataset import parkingHandler , electricChargePointHandler
    from persistence import cronologyHandler, preferenceHandler, userHandler
    print("BOT16")
    run()