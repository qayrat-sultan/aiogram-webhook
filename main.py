#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.
"""
6. Задание:

Создать команду /me Имя, в котором в качестве ответа выводится информация принадлежности
данного имени к какой то нации (попробуйте назвать, что Ваш учитель нацист:), я больше заданий дам)
https://api.nationalize.io/?name=gayrat
"""

import telebot
import requests
import pprint # noqa
from decouple import config
import pymongo

# BOT CONFIGS
API_TOKEN = config('TOKEN')
bot = telebot.TeleBot(API_TOKEN)

# DB CONFIGS
client = pymongo.MongoClient(config('MONGO'))
db = client.test
collusers = db.users
collbans = db.bans
collfunc = db.func



def natist_g(name):
    get_natist = requests.get(f'https://api.nationalize.io/?name={name}')
    result = get_natist.json()
    x = ''
    for i in result['country']:
        country_pr = (i['country_id'], i['probability'])
        x = x + str(country_pr)
    return x


def bitcoin_rate():
    get_btc = requests.get('https://api.coinbase.com/v2/prices/USD/spot')
    data = get_btc.json()['data']
    for i in data:
        if i.get('base') == 'BTC':
            print(i)
            return i


def music(parametr):
    get_artist = requests.get(f'https://itunes.apple.com/search?term={parametr}&media=music&limit=10')
    data = get_artist.json()['results']
    songs = ''
    for i in data:
        songs += i['trackName'] + '\n'
    return songs

    # pprint.pprint(data)


def universities():
    get_univ = requests.get('http://universities.hipolabs.com/search?country=Uzbekistan')
    univ_str = ''
    data = get_univ.json()
    print(data)
    for num, i in enumerate(data):
        if num < 6:
            univer_site = ''
            for j in i['web_pages']:
                univer_site += j + " "
            univ_str += (f"Univer name: {i['name']}\n web_pages: "
                         f"{univer_site}" + '\n\n')
    return univ_str


# universities()
# Handle '/start' and '/help'

def user():
    get_user = requests.get('https://randomuser.me/api/')
    data = get_user.json()['results']
    full_user_data = ''
    for i in data:
        full_name = i['name']
        full_name_str = f'Name: {full_name["first"]} '
        location = i['location']
        location_str = f'Country:  {location["country"]}'
        username = i['login']['username']
        password = i['login']['password']
        login = f'Username: {username}, Password: {password}'
        full_user_data += f'{full_name_str}\n{location_str} \n{login}'
        print(full_user_data)
    return full_user_data


@bot.message_handler(commands=['user'])
def send_random_user(message):
    x = user()
    func_user = collfunc.find_one({"id": message.chat.id})
    if not func_user:
        collfunc.insert_one({"id": message.chat.id, "func": "user", "count": 1})
    else:
        # counter = func_user['count']  # 1
        collfunc.update_one({"id": message.chat.id}, {"$inc": {"count": 1}})
    bot.send_message(message.chat.id, x)


@bot.message_handler(commands=['start'])
def send_random_user(message):
    user_id = collusers.find_one({"id": message.chat.id})
    if not user_id:
        collusers.insert_one({'id': message.chat.id,
                              'name': message.from_user.first_name})
    bot.send_message(message.chat.id, "Hello")


@bot.message_handler(commands=['del'])
def delete_user_data_from_db(msg):
    bot.send_message(msg.chat.id, "Successfully deleted!")
    collusers.delete_one({"id": msg.chat.id})


@bot.message_handler(commands=['update'])  # /update New_name
def update_user_data_from_db(message):
    updated_name = message.text.split()
    if len(updated_name) > 1:
        x = updated_name[1]
        collusers.update_one({"id": message.chat.id}, {"$set": {"name": x}})  # first dict is finding collection, second setting collection
        bot.send_message(message.chat.id, "Successfully updated!")
    else:
        bot.send_message(message.chat.id, "Please send me supported command For example:\n/me *Name*", parse_mode="MarkdownV2")

@bot.message_handler(commands=['help'])
def help_text(message):
    bot.send_message(message.chat.id, "/me {имя} - Команда для того чтобы определить к какой нации относится данное имя")

@bot.message_handler(commands=['me'])
def send_random_user(message):
    # natist_name = message.from_user.first_name
    natist_name = message.text.split()
    if len(natist_name) > 1:
        natist_name = natist_name[1]
        x = natist_g(natist_name)
        bot.send_message(message.chat.id, x)
    else:
        bot.send_message(message.chat.id, "Please send me supported command For example:\n/me *Name*", parse_mode="MarkdownV2")


@bot.message_handler(func=lambda message: message.text == "Регистрация")
def send_welcome(message: telebot.types.Message):
    p = bot.send_message(message.chat.id, "Введите Ваше имя")
    bot.register_next_step_handler(p, set_min_reg)


def set_min_reg(message: telebot.types.Message):
    name = message.text
    x = collusers.find_one({"id": message.chat.id})
    collusers.update_one({"id": message.chat.id}, {"$set": {"id": message.chat.id, "name": name}})

    bot.send_message(message.chat.id, "SUCCESSFULLY CHANGED")
    # retype = bot.send_message(message.chat.id,
    #                           "Минимальный возраст должен состоять только из цифр")
    # bot.register_next_step_handler(retype, set_min_reg)


def set_max_age(message):
    if not message.text.isdigit():
        retype = bot.send_message(message.chat.id,
                                  "Максимальный возраст должен состоять только из цифр")
        bot.register_next_step_handler(retype, set_max_age)
    else:
        ## pass save method for this DB
        bot.send_message(message.chat.id, "Успешно сохранен")


@bot.message_handler(commands=['btc'])
def send_btc_rate(message):
    btc = bitcoin_rate()  # dict
    bot.send_message(message.chat.id, f"Bitcoint currency: {btc['amount']}")


@bot.message_handler(commands=['music'])
def send_songs(message):
    x = message.text.split()
    music_get = music(x)
    bot.send_message(message.chat.id, music_get)


@bot.message_handler(commands=['univer'])
def send_songs(message):
    univ_str = universities()
    bot.send_message(message.chat.id, univ_str, disable_web_page_preview=True)


def weather():
    get_weather = requests.get('https://www.7timer.info/bin/astro.php?lon=69.2&lat=41.3&ac=0&unit=metric&output=json')
    data = get_weather.json()
    return data['dataseries'][0]['temp2m']


@bot.message_handler(commands=['pogoda'])
def send_weather_temp(message):
    # pprint.pprint(message.json)
    # print(message.text.split())
    x = weather()  # dict
    # bitcoin_rate()
    bot.send_message(message.chat.id, f"Weather temp: {x}  {weather()}")
    print(x)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    print(message.text)
    bot.reply_to(message, message.text)


# bot.enable_save_next_step_handlers(delay=2)
# bot.load_next_step_handlers()

print("Bot started")

bot.infinity_polling()
