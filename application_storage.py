from __future__ import annotations

from application import Application
from typing import Set, Dict, Tuple

import datetime
import telebot
import logging


def update_last_access(func):
    def wrapper(self: ApplicationStorage, *args, **kwargs):
        new_last_access = datetime.datetime.now()
        if new_last_access.day != self.last_access.day:
            self.clean_application()
        
        self.last_access = datetime.datetime.now()
        return func(self, *args, **kwargs)
    return wrapper


class ApplicationStorage:
    def __init__(self, bot: telebot.TeleBot):
        self.last_access = datetime.datetime.now()
        self.applications : Set[Application] = set()
        self.hanging_matches : Dict[int, Tuple[Application, Application]] = dict()
        self.bot = bot

    def clean_application(self):
        self.applications.clear()
        self.hanging_matches.clear()

    @update_last_access
    def add_application(self, application: Application):
        logging.info(f"Add application {application}")
        for active_application in self.applications:
            self.try_match(application, active_application)
        self.applications.add(application)


    @update_last_access
    def remove_application(self, application: Application):
        logging.info(f"Remove application {application}")
        self.applications.remove(application)
    
    @update_last_access
    def process_possible_match(self, trigger_message_id: int) -> bool:
        if trigger_message_id not in self.hanging_matches:
            logging.warning(f"Message {trigger_message_id} not in hanging matches")
            return False
        
        trigger_application, active_application = self.hanging_matches.pop(trigger_message_id)
        if trigger_application not in self.applications or active_application not in self.applications:
            logging.info(f"Application {trigger_application} or {active_application} not active anymore")

            if trigger_application in self.applications:
                self.bot.send_message(trigger_application.chat.id, "Похоже игрок нашел себе другую игру :с")
            elif active_application in self.applications:
                self.bot.send_message(active_application.chat.id, "Похоже игрок нашел себе другую игру :с")

            return False

        self.bot.send_message(trigger_application.chat.id, f"Это мэтч! Приятной игры с игроком @{active_application.user.username}! Если захотите сыграть ещё раз, нажмите /find")
        self.bot.send_message(active_application.chat.id, f"Это мэтч! Приятной игры с игроком @{trigger_application.user.username}! Если захотите сыграть ещё раз, нажмите /find")
        self.remove_application(trigger_application)
        self.remove_application(active_application)
        return True

    def try_match(self, trigger_application: Application, active_application: Application):
        markup = telebot.types.InlineKeyboardMarkup()
        accept = telebot.types.InlineKeyboardButton("Играем!", callback_data="accept")
        markup.add(accept)
        message = self.bot.send_message(active_application.chat.id, f"Игрок @{trigger_application.user.username} ищет игру!", reply_markup=markup)
        self.hanging_matches[message.id] = (trigger_application, active_application)
