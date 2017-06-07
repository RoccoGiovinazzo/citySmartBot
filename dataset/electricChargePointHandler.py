'''
Created on 06 giu 2017

@author: ROCCO
'''

import json
import urllib
import telegram
import numpy as np
from telegram.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.keyboardbutton import KeyboardButton
from bot.models import User, Cronology, Preference
import main
import numpy as np
from persistence import cronologyHandler, userHandler
from persistence.preferenceHandler import addPreferencesKeyboard
import utility



def chargePoint(bot, update):
    user = User.objects.get(chat_id=update.message.chat_id)
    User.objects.filter(chat_id=update.message.chat_id).update(lastCommand = "chargePoint")
    cronologyHandler.createCronology(bot, update, user)
    locationGPS_keyboard = KeyboardButton(text="Send my GPS location", request_location=True)
    locationUser_keyboard = KeyboardButton(text="Choose another location")
    custom_keyboard = [[ locationGPS_keyboard], [locationUser_keyboard]]
    addPreferencesKeyboard(custom_keyboard, user)
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)
    bot.sendMessage(chat_id=update.message.chat_id, text="Would you mind sharing your location to search the closest charge point?", reply_markup=reply_markup)


def calculate_charge_point_distance(bot, update, chargePoints):
    utente = User.objects.get(chat_id=update.message.chat_id)
    lat = utente.lat
    lon = utente.lon
    distanceArray = []
    for p in chargePoints:
        distance = utility.haversine(lon, lat, p['geometry']['coordinates'][0], p['geometry']['coordinates'][1])
        distanceArray.append(distance)
    arrDist = np.array(distanceArray)
    arrDist.sort()
    arrDist = arrDist[:3]
    arr = np.array(distanceArray)
    return arr.argsort()[:3], arrDist


def chargePointResult(bot, update):
    user = User.objects.get(chat_id=update.message.chat_id)
    geocode_result = main.gmaps.geocode(user.positionName)
    if geocode_result:
        address = geocode_result[0]['formatted_address']
        message = "You inserted this location " + address
        latid = geocode_result[0]['geometry']['location']['lat']
        long = geocode_result[0]['geometry']['location']['lng']
        User.objects.filter(chat_id=update.message.chat_id).update(lat=latid, lon=long)
        bot.sendMessage(chat_id=update.message.chat_id, text=message)
        location(bot, update)
    else:
        message = "I couldn't find this location. \nType again"
        User.objects.filter(chat_id=update.message.chat_id).update(lastCommand='chargePoint')
        bot.sendMessage(chat_id=update.message.chat_id, text=message)

def location(bot, update):
    urld = 'https://kaart.amsterdam.nl/datasets/datasets-item/t/parkeerlocaties-1/export/json'
    user = User.objects.get(chat_id=update.message.chat_id)
    User.objects.filter(chat_id=update.message.chat_id).update(lastCommand="chargePoint")
    cronologyHandler.createCronology(bot, update, user)
    r = urllib.request.urlopen(urld)
    data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
    closestChargePoints, closestDistance = calculate_charge_point_distance(bot, update, data['features']);    
    url, keyboard = utility.getDecoratedMap(bot, update, closestChargePoints, data['features'], closestDistance)
    reply_markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    #bot.sendPhoto(chat_id = update.message.chat_id, photo=url)
    bot.sendMessage(chat_id = update.message.chat_id, text="Choose for more details: ", reply_markup=reply_markup)
    reply_markup = telegram.ReplyKeyboardRemove()
    userHandler.setUserBotActived(update.message.chat_id, True)
    
def sendMessageForChargePoints(closestChargePoints, data, bot, update):
    emoticons = [utility.ONE_KEYCAP, utility.TWO_KEYCAP, utility.THREE_KEYCAP]
    i=0
    for p in closestChargePoints:
        message = emoticons[i] + " The charge point is: " + data[p]['properties']['title'] + "\n"
        bot.sendLocation(update.message.chat_id, data[p]['geometry']['coordinates'][1], data[p]['geometry']['coordinates'][0])
        keyboard = [[InlineKeyboardButton("Show Details", callback_data= str(p))]]         
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text=message, reply_markup=reply_markup) 
        i += 1
    bot.sendMessage(chat_id=update.message.chat_id, text = "Click on show details to get more informations or start a new search typing /charge point")  

def sendMessageForSingleChargePoint(bot, update, index):
    urld = 'https://kaart.amsterdam.nl/datasets/datasets-item/t/parkeerlocaties-1/export/json'
    # utente.lastCommand = "location"
    r = urllib.request.urlopen(urld)
    data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
    message = "<b>The charge point is: </b>" + data['features'][int(index)]['properties']['title'] + "\n"
#     try:
#         message += "<b>Free short parkings: </b>" + str(data['features'][int(index)]['properties']['layers']['parking.garage']['data']['FreeSpaceShort']) + "\n"
#     except KeyError:
#         message += "<b>Free short parkings: </b>" + '---' + "\n"
#     try:
#         message += "<b>Free long parkings: </b>" + str(data['features'][int(index)]['properties']['layers']['parking.garage']['data']['FreeSpaceLong']) + "\n"
#     except KeyError:
#        message += "<b>Free long parkings: </b>" + '---' + "\n"
    reverse_geocode_result = main.gmaps.reverse_geocode((data['features'][int(index)]['geometry']['coordinates'][1], data['features'][int(index)]['geometry']['coordinates'][0]))
    message += "<b>The address of the charge point is: </b>" + reverse_geocode_result[0]['formatted_address']
    bot.sendLocation(update.message.chat_id, data['features'][int(index)]['geometry']['coordinates'][1], data['features'][int(index)]['geometry']['coordinates'][0]) 
    bot.sendMessage(chat_id=update.message.chat_id, text = message, parse_mode='HTML')
    latid = data['features'][int(index)]['geometry']['coordinates'][1]
    long = data['features'][int(index)]['geometry']['coordinates'][0]
    User.objects.filter(chat_id=update.message.chat_id).update(lat=latid, lon=long)
    User.objects.filter(chat_id=update.message.chat_id).update(lastCommand = "chargePoint.afterDetails")
    User.objects.filter(chat_id=update.message.chat_id).update(positionName = reverse_geocode_result[0]['formatted_address'])
    bot.sendMessage(chat_id=update.message.chat_id, text = 'What do you want to do now?')
    userHandler.setUserBotActived(update.message.chat_id, True)