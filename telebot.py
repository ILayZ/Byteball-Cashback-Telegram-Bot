import os
import sys
from threading import Thread

import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler,MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

import visionocr
import os
from CREDENTIALS import BOT_KEY #, USER_DATA
CONFIG = 'user_data.json'

import logging
import re
import requests
from dbhelper import DBHelper
import json

db = DBHelper()

# Enable logging
logging.basicConfig(#format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG
                    #,filename = u'cashbot.log'
                    )

logger     = logging.getLogger(__name__)
#bot        = telegram.Bot(token=BOT_KEY)

# Global vars:
BOT_NAME = "ByteballCashbackBot"
LANG = "EN"
#SET_LANG, MENU, SET_STATE =  range(3)
#STATE = SET_LANG
menu = {'send_addr': {'EN': 'Provide BB address',
                      'RU': 'Введите BB адрес'
                     },
        'cashback': {'EN': 'Cashback',
                     'RU': 'Скидка'
                    }
       }

def start(bot,update,user_data):
    logger.warning('Entering: start')
    # Read default values for request and address, if we saved it
    with open(CONFIG) as f:
         USER_DATA = json.load(f)
    user_data.update(USER_DATA)
    # Create buttons for menu:    
    keyboard = [['/start','/cashback']]
    #keyboard.append([user_data['address']])

    # Create initial message:
    user = update.message.from_user
    msg = "Hey " + user.first_name + ", send me check photo / Byteball address and I'll send you cashback!"

    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    bot.send_message(chat_id=update.message.chat_id, text=msg, reply_markup=reply_markup)
    #
    user_data['customer'] = str(user.first_name) + ' ' + str(user.last_name) + ' ' + str(user.username)
    logger.warning(str(user_data))
    logger.warning('Exiting: start')

def cashback(bot,update,user_data):
    logger.warning('Entering: cashback')
    logger.warning(str(user_data))
    r = requests.post("https://byte.money/new_purchase", data=user_data)
    logger.warning(r.status_code)
    if r.status_code != '200':
       logger.warning(r.reason)
    bot.send_message(chat_id=update.message.chat_id, text=r.text)
    logger.warning('Exiting: cashback')

def error(bot, update, error):
    #Log Errors caused by Updates
    logger.warning('Update "%s" caused error "%s"', update, error)

def echo(bot, update, user_data):
    logger.warning('Entering: echo')
    msg = update.message
    chat_id = update.message.chat_id
    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    byteball_address = re.search(r':(\w{32})', msg.text).group(1)
    #logger.warning(byteball_address)
    if byteball_address:
        text = "Your Byteball address: " + byteball_address
        #logger.warning(str(user_data))
        user_data['address'] = byteball_address
        #logger.warning(str(user_data))
        #with open(CONFIG, 'w') as f:
        #    json.dump(user_data, f)
    else:
        text = "Try sending me a check photo or Byteball address!"
    bot.send_message(chat_id=chat_id, text=text)
   #logger.warning(str(user_data))
    logger.warning('Exiting: echo')

def receive_doc(bot,update,user_data):
    message = update.message
    file_id = message.document.file_id
    chat_id = update.message.chat_id
    ocr_file(bot,update,file_id,chat_id)

def receive_image(bot,update,user_data):
    logger.warning('Entering: receive_image')
    message = update.message
    file_id = message.photo[-1].file_id
    chat_id = update.message.chat_id
    logger.warning("file_id = " + str(file_id))
    logger.warning("chat_id = " + str(chat_id))
    ocr_file(bot,update,file_id,chat_id,user_data)
    logger.warning('Exiting: receive_image')
    
def ocr_file(bot,update,file_id,chat_id,user_data):
    filepath = os.path.expanduser('~') + '/' + file_id
    logger.warning("filepath = " + filepath)
    bot.send_message(chat_id=chat_id, text="Please hold on...")
    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    file = bot.get_file(file_id).download(filepath)
    
    ocr_text = visionocr.read_image(filepath)
    logger.warning(str(ocr_text))
    parse_ocr(bot,chat_id,str(ocr_text),user_data)
    os.remove(filepath)

def parse_ocr(bot,chat_id,ocr_text,user_data):
    try:
        inn    = re.search(r'ИНН\s+([\d|\s]{12})' , ocr_text).group(1)
    except Exception as e:
        logger.warning(e)
    try:
        check  = re.search(r'(Чек)(.*\s)(\d+)[\n|\s]+'  , ocr_text).group(3)
    except Exception as e:
        logger.warning(e)
    try:
        date   = re.search(r'(\d\d-\d\d-\d\d\d\d)', ocr_text).group(1)
    except Exception as e:
        logger.warning(e)
    try:
        time   = re.search(r'Закрыт\s+(\d\d:\d\d)', ocr_text).group(1)
    except Exception as e:
        logger.warning(e)        

    amount = re.search(r'Итого:\n(\d+\.\d\d)' , ocr_text).group(1)
    #
    user_data['merchant'] = inn
    user_data['order_id'] = date + ' ' + time + ' ' + check 
                           #user_data['customer'] + ' ' + date
    user_data['currency_amount'] = amount
    #i = 0
    #desc = ''
    #for line in ocr_text.splitlines() :
    #    i += 1
    #    if line == 'Всего:':
    #        break
    #    if i > 12 and re.search(r'\D+', line):
    #        desc += line + ' '
    try:
        user_data['description'] = re.search(r'(Блюдо\nКол-во\nСумма\n)(.*\n)(Всего:\n)' , ocr_text, flags=re.DOTALL ).group(2)
    except Exception as e:
        logger.warning(e)
        user_data['description'] = 'Error'
    
    logger.warning(str(user_data))
    #
    bot.send_message(chat_id=chat_id, text='Here you go:\n\n' + str(user_data))
    db.add(user_data)

def set_state(bot, update, user_data):
    """
    Set option selected from menu.
    """
    # Set state:
    global STATE
    user = update.message.from_user
    if update.message.text == menu['send_addr'][LANG]:
        STATE = SEND_ADDR
        send_addr(bot, update, user_data)
        return MENU
    elif update.message.text == menu['about'][LANG]:
        STATE = ABOUT
        about_bot(bot, update, user_data)
        return MENU
    else:
        STATE = MENU
    return MENU

def main():
    # Create table and index
    db.setup()

    # Create the EventHandler and pass it your bot's token.
    updater    = Updater(token=BOT_KEY)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # handlers
    start_handler    = CommandHandler('start',         start,        pass_user_data=True)
    cashback_handler = CommandHandler('cashback',      cashback,     pass_user_data=True)
    echo_handler     = MessageHandler(Filters.text,    echo,         pass_user_data=True)
    doc_handler      = MessageHandler(Filters.document,receive_doc,  pass_user_data=True)
    image_handler    = MessageHandler(Filters.photo,   receive_image,pass_user_data=True)

    # Add conversation handler with predefined states:
    """conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True)],

        states={
            #SET_LANG: [RegexHandler('^(RU|EN)$', set_lang)],

            #MENU: [CommandHandler('menu', menu, pass_user_data=True)],

            SET_STATE: [RegexHandler(
                        '^({}|{}|{}|{})$'.format(
                            send_addr('EN'), cashback('EN'),
                            #view_faq['EN'], view_about['EN']),
                        set_state)],

            SEND_CHECK: [MessageHandler(Filters.photo, receive_image, pass_user_data=True),
                         CommandHandler('menu', menu)]
        },

        fallbacks=[CommandHandler('cancel', cancel),
                   CommandHandler('help', help)]
    )"""

    #dispatchers
    dp.add_handler(start_handler)
    dp.add_handler(cashback_handler)
    dp.add_handler(echo_handler)
    dp.add_handler(doc_handler)
    dp.add_handler(image_handler)
    #log all errors
    dp.add_error_handler(error)

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(bot, update):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    dp.add_handler(CommandHandler('r', restart, filters=Filters.user(username='@ILayZ')))

    # Start the Bot
    updater.start_polling()

    #Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
