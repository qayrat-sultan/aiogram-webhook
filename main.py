#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.
"""
6. Задание:

Создать команду /me Имя, в котором в качестве ответа выводится информация принадлежности
данного имени к какой то нации (попробуйте назвать, что Ваш учитель нацист:), я больше заданий дам)
https://api.nationalize.io/?name=gayrat
"""
import logging
# import telebot
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.executor import start_webhook
import requests
import pprint # noqa
from decouple import config
import pymongo

# BOT CONFIGS
API_TOKEN = config('TOKEN')

# webhook settings
WEBHOOK_HOST = 'https://webhooktgbot.herokuapp.com'
WEBHOOK_PATH = '/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = 'localhost'  # or ip
WEBAPP_PORT = 3001


# bot = telebot.TeleBot(API_TOKEN)
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# DB CONFIGS
client = pymongo.MongoClient(config('MONGO'))
db = client.test
collusers = db.users
collbans = db.bans
collfunc = db.func


async def natist_g(name):
    get_natist = requests.get(f'https://api.nationalize.io/?name={name}')
    result = get_natist.json()
    x = ''
    for i in result['country']:
        country_pr = (i['country_id'], i['probability'])
        x = x + str(country_pr)
    return x


async def bitcoin_rate():
    get_btc = requests.get('https://api.coinbase.com/v2/prices/USD/spot')
    data = get_btc.json()['data']
    for i in data:
        if i.get('base') == 'BTC':
            print(i)
            return i


async def music(parametr):
    get_artist = requests.get(f'https://itunes.apple.com/search?term={parametr}&media=music&limit=10')
    data = get_artist.json()['results']
    songs = ''
    for i in data:
        songs += i['trackName'] + '\n'
    return songs

    # pprint.pprint(data)


async def universities():
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


# await universities()
# Handle '/start' and '/help'

async def user():
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


@dp.message_handler(commands=['user'])
async def send_random_user(message):
    x = user()
    func_user = collfunc.find_one({"id": message.chat.id})
    if not func_user:
        collfunc.insert_one({"id": message.chat.id, "func": "user", "count": 1})
    else:
        # counter = func_user['count']  # 1
        collfunc.update_one({"id": message.chat.id}, {"$inc": {"count": 1}})
    await bot.send_message(message.chat.id, x)


@dp.message_handler(commands=['start'])
async def send_random_user(message):
    user_id = collusers.find_one({"id": message.chat.id})
    if not user_id:
        collusers.insert_one({'id': message.chat.id,
                              'name': message.from_user.first_name})
    await bot.send_message(message.chat.id, "Hello")


@dp.message_handler(commands=['del'])
async def delete_user_data_from_db(msg):
    await bot.send_message(msg.chat.id, "Successfully deleted!")
    collusers.delete_one({"id": msg.chat.id})


@dp.message_handler(commands=['update'])  # /update New_name
async def update_user_data_from_db(message):
    updated_name = message.text.split()
    if len(updated_name) > 1:
        x = updated_name[1]
        collusers.update_one({"id": message.chat.id}, {"$set": {"name": x}})  # first dict is finding collection, second setting collection
        await bot.send_message(message.chat.id, "Successfully updated!")
    else:
        await bot.send_message(message.chat.id, "Please send me supported command For example:\n/me *Name*",
                         parse_mode="MarkdownV2")


@dp.message_handler(commands=['help'])
async def help_text(message):
    await bot.send_message(message.chat.id,
                     "/me {имя} - Команда для того чтобы определить к какой нации относится данное имя")


@dp.message_handler(commands=['me'])
async def send_random_user(message):
    # natist_name = message.from_user.first_name
    natist_name = message.text.split()
    if len(natist_name) > 1:
        natist_name = natist_name[1]
        x = await natist_g(natist_name)
        await bot.send_message(message.chat.id, x)
    else:
        await bot.send_message(message.chat.id, "Please send me supported command For example:\n/me *Name*",
                         parse_mode="MarkdownV2")


@dp.message_handler(lambda message: "Регистрация" in message.text)
async def send_welcome(message: types.Message):
    p = await bot.send_message(message.chat.id, "Введите Ваше имя")
    await bot.register_next_step_handler(p, set_min_reg)


async def set_min_reg(message: types.Message):
    name = message.text
    x = collusers.find_one({"id": message.chat.id})
    collusers.update_one({"id": message.chat.id}, {"$set": {"id": message.chat.id, "name": name}})

    await bot.send_message(message.chat.id, "SUCCESSFULLY CHANGED")
    # retype = await bot.send_message(message.chat.id,
    #                           "Минимальный возраст должен состоять только из цифр")
    # bot.register_next_step_handler(retype, set_min_reg)


async def set_max_age(message):
    if not message.text.isdigit():
        retype = await bot.send_message(message.chat.id,
                                  "Максимальный возраст должен состоять только из цифр")
        bot.register_next_step_handler(retype, set_max_age)
    else:
        ## pass save method for this DB
        await bot.send_message(message.chat.id, "Успешно сохранен")


@dp.message_handler(commands=['btc'])
async def send_btc_rate(message):
    btc = await bitcoin_rate()  # dict
    await bot.send_message(message.chat.id, f"Bitcoint currency: {btc['amount']}")


@dp.message_handler(commands=['music'])
async def send_songs(message):
    x = message.text.split()
    music_get = music(x)
    await bot.send_message(message.chat.id, music_get)


@dp.message_handler(commands=['univer'])
async def send_songs(message):
    univ_str = await universities()
    await bot.send_message(message.chat.id, univ_str, disable_web_page_preview=True)


async def weather():
    get_weather = requests.get('https://www.7timer.info/bin/astro.php?lon=69.2&lat=41.3&ac=0&unit=metric&output=json')
    data = get_weather.json()
    return data['dataseries'][0]['temp2m']


@dp.message_handler(commands=['pogoda'])
async def send_weather_temp(message):
    # pprint.pprint(message.json)
    # print(message.text.split())
    x = weather()  # dict
    # bitcoin_rate()
    await bot.send_message(message.chat.id, f"Weather temp: {x}  {weather()}")
    print(x)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@dp.message_handler()
async def echo_message(message):
    print(message.text)
    await message.answer(message.text)


# bot.enable_save_next_step_handlers(delay=2)
# bot.load_next_step_handlers()


async def on_startup(dp):
    print("Bot started")

async def on_shutdown(dp):
    print("Bot stopped")
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
