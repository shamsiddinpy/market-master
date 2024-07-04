#!/usr/bin/python
import os
from random import randint

import django
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')
django.setup()

bot = telebot.TeleBot('7191574421:AAHJwnWrKzSGBfA7Qjxc99BOxDB1QySq_00')

from apps.models import User
from django.core.cache import cache


def set_code(phone: str):
    code = randint(100_000, 999_999)
    while cache.get(code):
        code = randint(100_000, 999_999)
    cache.set(code, phone, timeout=60)
    cache.set(phone, code, timeout=60)
    return code


@bot.message_handler(commands=['login'])
def send_welcome(message):
    try:
        user = User.objects.get(telegram_id=message.from_user.id)
        code = cache.get(user.phone)
        if code:
            text = f"Eski kodingiz hali ham kuchda ☝️"
            bot.send_message(message.chat.id, text)
        else:
            code = set_code(user.phone)
            text = f'🔒 Kodingiz: \n```{code}```'
            inline_kb = InlineKeyboardMarkup()
            inline_btn = InlineKeyboardButton('Yangi parol olish', callback_data='new_password')
            inline_kb.add(inline_btn)
            bot.send_message(message.chat.id, text, parse_mode='MarkdownV2', reply_markup=inline_kb)
    except User.DoesNotExist:
        bot.send_message(message.chat.id,
                         "Foydalanuvchi topilmadi. Iltimos, avval /start orqali kontaktingizni yuborish orqali "
                         "ro'yxatdan o'ting.")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not User.objects.filter(telegram_id=message.from_user.id).exists():
        text = f"""
        Salom {message.from_user.first_name} 👋
        @market_sh botiga xush kelibsiz...
        ⬇ Kontaktingizni yuboring (tugmani bosing..)
        """
        rkm = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        rkm.add(KeyboardButton('Kontakt Yuborish', request_contact=True))
        bot.send_message(message.chat.id, text, reply_markup=rkm)
    else:
        text = '🔑 Yangi kod olish uchun /login ni bosing'
        bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=['contact'])
def echo_message(message):
    phone_number = message.contact.phone_number[-9:]
    obj, created = User.objects.get_or_create(phone=phone_number)
    obj.first_name = message.from_user.first_name
    obj.telegram_id = message.from_user.id
    user_photo = bot.get_user_profile_photos(message.from_user.id)
    print(user_photo)
    obj.save()
    code = set_code(obj.phone)
    text = f'🔒 Kodingiz:\n```{code}```'
    inline_kb = InlineKeyboardMarkup()
    inline_btn = InlineKeyboardButton('Yangi parol olish', callback_data='new_password')
    inline_kb.add(inline_btn)
    bot.send_message(message.chat.id, text, parse_mode='MarkdownV2', reply_markup=inline_kb)


@bot.callback_query_handler(func=lambda call: call.data == 'new_password')
def handle_new_password(call):
    try:
        user = User.objects.get(telegram_id=call.from_user.id)
        code = cache.get(user.phone)
        if code:
            text = f"Eski kodingiz hali ham kuchda ☝️"
            bot.send_message(call.message.chat.id, text)
        else:
            code = set_code(user.phone)
            text = f'🔒 Yangi kodingiz: \n```{code}```'
            inline_kb = InlineKeyboardMarkup()
            inline_btn = InlineKeyboardButton('Yangi parol olish', callback_data='new_password')
            inline_kb.add(inline_btn)
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='MarkdownV2',
                                  reply_markup=inline_kb)
    except User.DoesNotExist:
        bot.send_message(call.message.chat.id,
                         "Foydalanuvchi topilmadi. Iltimos, avval /start orqali kontaktingizni yuborish orqali "
                         "ro'yxatdan o'ting.")


bot.infinity_polling()
