import os
import telebot 
import requests
import datetime
from datetime import datetime, timedelta
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

from settings import *
from sql_control import *

'''
Exchange function is unvailable in free account
'''

bot = telebot.TeleBot(token)

#When last request was. If <10, we get data from local db. Else, we write new data to db
def time_check():
    lastrequest = datetime.fromtimestamp(get_time())
    delta = datetime.now() - lastrequest
    if delta > timedelta(minutes=10):
        url ='http://api.exchangeratesapi.io/v1/latest?access_key=' + api_key + '&symbols=USD,CAD,GBP'
        data = requests.get(url).json()
        wrtitedb(data)
        data = pd.DataFrame(data)
        data = data.reset_index()
    elif delta < timedelta(minutes=10):
        data = get_rates()
    return data


def get_latest_rate():
    data = time_check()
    cur = 'Base currency:  EUR' + '\nExchange List:\n' 
    for index, row in data.iterrows():
        print(row['rates'], row['index'])
        cur += '    ' +  row['index'] + ':  ' + str(round(row['rates'],2)) + '\n'
    return cur


def get_seven_days_rate(currency):
    today = DT.date.today()
    i=7
    df = pd.DataFrame()
    while True:
        week_ago = today - DT.timedelta(days=i)
        url = 'http://api.exchangeratesapi.io/v1/' + str(week_ago) + '?access_key=' + api_key + '&symbols=' + currency
        data = requests.get(url).json()
        day_data = pd.DataFrame(data)
        df = df.append(day_data)
        i = i - 1
        if i == 0:
            df = df.reset_index()
            df.plot(x ='date', y=['rates'], kind = 'line')
            plt.savefig('plot.png')
            break


def get_state(message):
    return USER_STATE[message.chat.id]


def update_state(message, state):
    USER_STATE[message.chat.id] = state


def symbol_check(symbol):
    url ='http://api.exchangeratesapi.io/v1/latest?access_key=' + api_key + '&symbols=' + symbol
    data = requests.get(url).json()
    #API send back different response for successful and unsuccessful requests
    try:
        return data['success']
    except KeyError:
        return False


#Hello for new user
@bot.message_handler(commands=['start'])
def hi(message):
    msg = 'List of available commands:\n    /list - recent exchange rates\n    /history - exchange rate graph for 7 days'
    bot.send_message(message.chat.id, msg)


#recent rates
@bot.message_handler(commands=['list'])
def lists(message):
    data = get_latest_rate()
    bot.send_message(message.chat.id, data)
    hi(message)


#Ask for symbol
@bot.message_handler(commands=['history'])
def history(message):
    bot.send_message(message.chat.id, 'Send currency symbol\n\nExample:USD')
    update_state(message, graph)


#Checks and graph
@bot.message_handler(func=lambda message: get_state(message) == graph)
def history(message):
    if symbol_check(message.text) == True:
        get_seven_days_rate(message.text)
        bot.send_photo(message.chat.id, photo=open(os.getcwd() + '\plot.png', 'rb'))
        hi(message)
        update_state(message, commands)
    elif symbol_check(message.text) == False:
        bot.send_message(message.chat.id, 'Invalid symbol. Try again')
    

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)