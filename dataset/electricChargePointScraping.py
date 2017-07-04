'''
Created on 27 giu 2017

@author: Geko
'''

from urllib.request import urlopen
from bs4 import BeautifulSoup as soup
import re

url = 'http://www.amsterdamtips.com/tips/parking-in-amsterdam.php'



def getElectricChargeCost():
    
    #open connection
    conn = urlopen(url)
    page_html = conn.read()
    conn.close()
    
    #parse the table
    page_soup = soup(page_html, "html.parser")
    tables = page_soup.findAll("table")
    parkingCost1 = extractData(tables[2])
    parkingCost2 = extractData(tables[3])
    parkingCost = parkingCost1 + parkingCost2
    print(parkingCost)
    return parkingCost

def extractData(table):
    rows = table.findChildren('tr')
    rows = rows[1:]

    rowFormatted = []
    
    for row in rows:
        cells = row.findChildren('td')
        rowFormatted.append([cells[1], cells[-1]])
    
    parkingCost = []    
    
    for row in rowFormatted:    
        rowClean = []
        for cell in row:
            
            value = list(cell.stripped_strings)
            string = ' '.join(value)
            string = string.split()
            string = ' '.join(string)
            #re.sub(r'[\t\n]]*', ' ', string)
            #regex = re.compile(r'[\n\r\t]')
            #regex.sub(' ', string)
            #print(string)
            rowClean.append(string)
            
        print('Valore riga: ' + str(rowClean))    
        parkingCost.append(rowClean)
    return parkingCost

