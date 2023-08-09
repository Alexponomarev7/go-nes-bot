from __future__ import annotations

import telebot

class Application:
    def __init__(self, user: telebot.types.User, chat: telebot.types.Chat):
        self.user = user
        self.chat = chat

    def __eq__(self, other: Application):
        return self.user.id == other.user.id and self.chat.id == other.chat.id

    def __hash__(self) -> int:
        return hash((self.user.id, self.chat.id))

    def __repr__(self) -> str:
        return f"Application(user={self.user.username}, chat={self.chat})"
