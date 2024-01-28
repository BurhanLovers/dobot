import json
import logging
import traceback
from os import environ
from typing import Union
import urllib.parse as urlparse
from urllib.parse import parse_qs

import telebot
from telebot.types import CallbackQuery, Message

from _bot import bot
# noinspection PyUnresolvedReferences
from modules import *

bot_admins = json.loads(environ.get('bot_admins'))

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

command_dict = {
    '/start': 'start',

    '/add_do': 'add_account',
    '/sett_do': 'manage_accounts',
    '/bath_do': 'batch_test_accounts',

    '/add_vps': 'create_droplet',
    '/sett_vps': 'manage_droplets',
    '/rebuild_vps': 'rebuild_vps_os',  # Tambahkan ini untuk menangani perintah /rebuild_vps
}

@bot.message_handler(content_types=['text'])
def text_handler(m: Message):
    try:
        logger.info(m)

        if m.from_user.id not in bot_admins:
            return

        if m.text in command_dict.keys():
            command_function = globals().get(command_dict[m.text])
            if command_function:
                if command_dict[m.text] == 'rebuild_vps':
                    rebuild_vps(m)  # Tambahkan argumen m ke fungsi rebuild_vps_os
                else:
                    command_function(m)
            else:
                bot.send_message(
                    chat_id=m.chat.id,
                    text="Perintah tidak ditemukan."
                )

    except Exception as e:
        traceback.print_exc()
        handle_exception(m, e)
