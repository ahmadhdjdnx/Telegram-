import telebot
import random
from telebot import types
import time
import threading

# توکن ربات خود را وارد کنید
TOKEN = "2071990345:AAG01uC1-V0zEy4YVBmLeaUA_l9SSG5rDgY"
bot = telebot.TeleBot(TOKEN)

# لیست کاربران منتظر
waiting_users = []
# لیست مکالمات فعال
active_chats = {}

# تولید آیدی یکتا (شش حرفی شامل اعداد و حروف انگلیسی)
def generate_unique_id():
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return ''.join(random.choice(chars) for _ in range(6))

# پیام خوش‌آمدگویی و تخصیص آیدی
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    unique_id = generate_unique_id()
    bot.send_message(user_id, "سلام! خوش آمدید. شما آماده استفاده از چت ناشناس هستید!", reply_markup=main_menu())

# ساخت منوی اصلی
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    connect_button = types.KeyboardButton("به یک ناشناس وصلم کن")
    markup.add(connect_button)
    return markup

# دکمه پایان چت
def chat_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    end_button = types.KeyboardButton("پایان چت")
    markup.add(end_button)
    return markup

# مدیریت درخواست اتصال
@bot.message_handler(func=lambda message: message.text == "به یک ناشناس وصلم کن")
def connect_user(message):
    user_id = message.chat.id

    # بررسی کاربر در حال چت نباشد
    if user_id in active_chats.keys():
        bot.send_message(user_id, "شما در حال حاضر در یک چت هستید. ابتدا چت را پایان دهید.")
        return

    # اضافه کردن کاربر به لیست منتظران
    waiting_users.append(user_id)
    bot.send_message(user_id, "منتظر بمانید تا یک ناشناس پیدا شود...")

    # بررسی اگر کاربر دیگری نیز منتظر است
    threading.Thread(target=try_connect, args=(user_id,)).start()

def try_connect(user_id):
    # یک دقیقه منتظر بمانید
    start_time = time.time()
    while time.time() - start_time < 60:
        if len(waiting_users) > 1:
            # پیدا کردن کاربر دیگر برای اتصال
            waiting_users.remove(user_id)
            partner_id = random.choice([u for u in waiting_users if u != user_id])
            waiting_users.remove(partner_id)

            # ذخیره مکالمه
            active_chats[user_id] = partner_id
            active_chats[partner_id] = user_id

            # اطلاع‌رسانی اتصال
            bot.send_message(user_id, "شما به یک ناشناس متصل شدید! شروع به صحبت کنید.", reply_markup=chat_menu())
            bot.send_message(partner_id, "شما به یک ناشناس متصل شدید! شروع به صحبت کنید.", reply_markup=chat_menu())
            return
        time.sleep(1)

    # اگر کسی پیدا نشد
    if user_id in waiting_users:
        waiting_users.remove(user_id)
        bot.send_message(user_id, "کسی برای چت پیدا نشد. دوباره امتحان کنید.")

# مدیریت پیام‌ها در چت
@bot.message_handler(func=lambda message: message.chat.id in active_chats.keys())
def relay_message(message):
    user_id = message.chat.id
    partner_id = active_chats[user_id]
    bot.send_message(partner_id, message.text)

# مدیریت پایان چت
@bot.message_handler(func=lambda message: message.text == "پایان چت")
def end_chat(message):
    user_id = message.chat.id

    # بررسی اینکه کاربر در چت باشد
    if user_id not in active_chats.keys():
        bot.send_message(user_id, "شما در هیچ چتی نیستید.")
        return

    # پایان چت
    partner_id = active_chats[user_id]
    del active_chats[user_id]
    del active_chats[partner_id]

    bot.send_message(user_id, "چت شما پایان یافت.", reply_markup=main_menu())
    bot.send_message(partner_id, "طرف مقابل چت را پایان داد.", reply_markup=main_menu())

# راه‌اندازی ربات
bot.polling(
