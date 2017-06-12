'''
Created on 31 mag 2017

@author: Geko
'''
from math import radians, asin, sin, cos, sqrt

from future.utils import bytes_to_native_str
from motionless import DecoratedMap, LatLonMarker
import six
from telegram.inlinekeyboardbutton import InlineKeyboardButton

import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from bot.models import User
from smartBot import settings


def getEmoticon(b):
    return bytes_to_native_str(b)

''' web source: '''
''' https://github.com/python-telegram-bot/python-telegram-bot/blob/master/telegram/emoji.py '''

ZERO_KEYCAP = getEmoticon(b'\x30\xE2\x83\xA3')
ONE_KEYCAP = getEmoticon(b'\x31\xE2\x83\xA3')
TWO_KEYCAP = getEmoticon(b'\x32\xE2\x83\xA3')    
THREE_KEYCAP = getEmoticon(b'\x33\xE2\x83\xA3')
FOUR_KEYCAP = getEmoticon(b'\x34\xE2\x83\xA3')
FIVE_KEYCAP = getEmoticon(b'\x35\xE2\x83\xA3')
SIX_KEYCAP = getEmoticon(b'\x36\xE2\x83\xA3')
SEVEN_KEYCAP = getEmoticon(b'\x37\xE2\x83\xA3')
EIGHT_KEYCAP = getEmoticon(b'\x38\xE2\x83\xA3')
NINE_KEYCAP = getEmoticon(b'\x39\xE2\x83\xA3')

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km

def getDecoratedMap(bot, update, closestParkings, data, distances):
    road_styles = [{
    'feature': 'road.highway',
    'element': 'geomoetry',
    'rules': {
        'visibility': 'simplified',
        'color': '#c280e9'
    }
    }, {
    'feature': 'transit.line',
    'rules': {
        'visibility': 'simplified',
        'color': '#bababa'
    }
    }]
    dmap = DecoratedMap(style=road_styles)
    utente = User.objects.get(chat_id=update.message.chat_id)
    lat = utente.lat
    lon = utente.lon
    dmap.add_marker(LatLonMarker(lat, lon, label='S', color='blue'))
    i = 0
    keyboard = [[],[],[]]
    table = []
    for p in closestParkings:
        if "parking" in utente.lastCommand:
            dmap.add_marker(LatLonMarker(lat=data[p]['geometry']['coordinates'][1], lon=data[p]['geometry']['coordinates'][0],label=str(i+1)))
            textButton = createDetailsButtonText(data[p], i)
            row = createRowParking(data[p], distances[i], i)
            
        elif "chargePoint" in utente.lastCommand:
            dmap.add_marker(LatLonMarker(lat=data[p]['geometry']['coordinates'][1], lon=data[p]['geometry']['coordinates'][0],label=str(i+1)))
            textButton = createDetailsButtonText(data[p], i)
            row = createRowChargePoint(data[p], distances[i], i)
            
        table.append(row)
        keyboard[i].append(InlineKeyboardButton(text=textButton, callback_data= str(p), resize_keyboard=True))
        i += 1
        
    url = dmap.generate_url()
    npArray = np.array(table)
    df = pd.DataFrame(npArray)
    df.columns = ['N.', 'Parking Name', 'Free Slots', 'Distance']
    ax = render_mpl_table(df, header_columns=0, col_width=1.5)
    fileName = str(update.message.chat_id) + '.png'
    plt.savefig(fileName, bbox_inches='tight')
    baseDir = settings.BASE_DIR
    picture = open(baseDir + '/' + fileName, 'rb')
    #img=urllib.request.urlopen(baseDir + '\foo.png').read()
    bot.sendPhoto(chat_id=update.message.chat_id, photo = picture)
    print(ax)
    return url, keyboard

def createDetailsButtonText(p, i):
    emoticons = [ONE_KEYCAP, TWO_KEYCAP, THREE_KEYCAP]
    text = str(p['properties']['title'])
    text = text[7:]
    text = emoticons[i] + ' - ' + text
    return text

def createRowParking(p, distance, index):
    row = []
    parkingName = p['properties']['title']
    row.append(index + 1)
    row.append(parkingName[7:])
    try:
        row.append(str(p['properties']['layers']['parking.garage']['data']['FreeSpaceShort']))
    except KeyError:
        row.append("No Info")
    row.append(str(float("{0:.2f}".format(distance))) + ' KM')
    return row

def createRowChargePoint(p, distance, index):
    row = []
    chargePointName = p['properties']['title']
    row.append(index + 1)
    row.append(chargePointName)
    try:
        row.append(str(p['properties']['layers']['parking.garage']['data']['FreeSpaceShort']))
    except KeyError:
        row.append("No Info")
    row.append(str(float("{0:.2f}".format(distance))) + ' KM')
    return row

def render_mpl_table(data, col_width=1.0, row_height=0.625, font_size=10,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='#414144',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, cellLoc='center', **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        text = cell.get_text().get_text()
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            print('Test width: ' + text)
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
        if k[1] == 0:
            cell.set_width(0.15)
        elif k[1] == 1:
            cell.set_width(0.6)
        elif k[1] == 2:
            cell.set_width(0.3)
        else:
            cell.set_width(0.3)
    return ax