#!/usr/bin/env python3
import telebot
import os
import argparse
import json
import logging

from application_storage import ApplicationStorage
from application import Application


TOKEN = os.environ["GO_NES_TOKEN"]
with open("scripts.json", "r") as f:
    SCRIPTS = json.load(f)

bot = telebot.TeleBot(TOKEN)
application_storage = ApplicationStorage(bot)


@bot.message_handler(commands=["start"])
def start(message: telebot.types.Message):
    print(message.__dict__)
    bot.send_message(message.chat.id, SCRIPTS["start"])

@bot.message_handler(commands=["find"])
def find(message: telebot.types.Message):
    if application_storage.add_application(Application(message.from_user, message.chat)):
        bot.send_message(message.chat.id, "Игра ищется!")
    else:
        bot.send_message(message.chat.id, "Вы уже ищете игру!")
    
@bot.message_handler(commands=["stop"])
def stop(message: telebot.types.Message):
    if application_storage.remove_application(Application(message.from_user, message.chat)):
        bot.send_message(message.chat.id, "Поиск игры остановлен!")
    else:
        bot.send_message(message.chat.id, "Вы не ищете игру!")

@bot.message_handler(commands=["help"])
def help(message: telebot.types.Message):
    bot.send_message(message.chat.id, SCRIPTS["help"])

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: telebot.types.CallbackQuery):
    if call.data == "accept":
        application_storage.process_possible_match(call.message.message_id)
    else:
        logging.error(f"Unknown callback data: {call.data}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-log-level", type=int, default=None)
    parser.add_argument("--log-level", type=str, default="INFO")
    args = parser.parse_args()

    if args.api_log_level:
        telebot.logger.setLevel(args.api_log_level)
    logging.basicConfig(level=logging._nameToLevel[args.log_level])

    bot.infinity_polling()
