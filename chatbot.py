from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters, ConversationHandler
from hiking import *
from tvshow import *
# from cookvideo import *
from urllib.parse import urlparse
import redis
# import os
import json
import logging
import configparser
from ChatGPT_HKBU import HKBU_ChatGPT

global redis1
config = configparser.ConfigParser()
config.read('config.ini')
redis1 = redis.Redis(host=(config['REDIS']['HOST']), 
                         password=(config['REDIS']['PASSWORD']), 
                         port=(config['REDIS']['REDISPORT']))



HIKING_OPTIONS, HIKING_READ, HIKING_WRITE, HIKING_READ_PHOTO  = range(4)
TVSHOW_READ_PHOTO, TVSHOW_WRITE_PROMPT, TVSHOW_WRITE, TVSHOW_END  = range(4)


def get_read_write_option(read_text, write_text, read, write):
    reply_keyboard_markup = InlineKeyboardMarkup(
        [
            [
            InlineKeyboardButton(
                text=read_text, callback_data=read),
            InlineKeyboardButton(
                text=write_text, callback_data=write)
            ]
        ]
    )
    return reply_keyboard_markup


def tvshow_photo(update, context):
    query = update.callback_query
    global randomShows
    try:
        if isinstance(query.data, int):
            tvshow_read(update, context)
        else:
            global tvReview
            tvReview = get_tv_review(query.data)
            if tvReview['image'] is not None:
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=tvReview['image'])
            if tvReview['review'] != 'review not found':
                context.bot.send_message(chat_id=update.effective_chat.id, text=tvReview['review'])
                reply_markup = get_read_write_option('Yes', 'No', str(TVSHOW_WRITE), str(TVSHOW_END))
                context.bot.send_message(chat_id=update.effective_chat.id, 
                                        text='Do you want to write the review of this show ?', reply_markup=reply_markup)
                return TVSHOW_WRITE_PROMPT
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, 
                                        text='Sorry, the selected TV cannot find in netflix, please try another one')
                tvshow_read(update, context)
    except:
        return tvshow_read(update, context)
  
def hiking_read(update, context):
    global randomPhotos
    hiking_information = get_hiking_information()
    btnOptions = []
    for index, locDesc in enumerate(hiking_information[0]):
        btnOptions.append( [InlineKeyboardButton(
                text=", ".join(locDesc), callback_data=index)])
    btnOptions.append( [InlineKeyboardButton(
                text="Give me other route", callback_data=len(hiking_information[0]))])
    reply_keyboard_markup = InlineKeyboardMarkup(btnOptions)
    randomPhotos = hiking_information[1]
    # context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Please select the hiking route", reply_markup=reply_keyboard_markup)
    return HIKING_READ_PHOTO

def hiking_photo(update, context):
    query = update.callback_query
    global randomPhotos
    try:
        index = int(query.data)
        photo = randomPhotos[int(query.data)]
        text = update.callback_query.message.reply_markup.inline_keyboard[index][0].text
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Here is the photo from {}".format(text))
        context.bot.send_message(chat_id=update.effective_chat.id, text='Click /start to try again')
        return ConversationHandler.END
    except:
        return hiking_read(update, context)
    
def hiking_write(update, context):
    message = update.message
    if len(message.photo) > 0 and message.caption is not None:
        photo_file = message.photo[-1].get_file()
        hiking_data = {
            "image" : photo_file.file_path,
            "id" : message.chat.id,
            "route" : message.caption
        }
        redis1.lpush("hiking", json.dumps(hiking_data))
        update.message.reply_text("Thank you for your share, Click /start to try again")
        return ConversationHandler.END
    else:
        update.message.reply_text("Hiking photo or caption is missing, please input again!")

def hiking_options(update, context):
    query = update.callback_query
    if query.data == str(HIKING_READ):
        return hiking_read(update, context)
    elif query.data == str(HIKING_WRITE):
        message = "Please share photo and input route information in the photo caption"
        context.bot.send_message(chat_id=update.effective_chat.id,  text=message)
        return int(query.data)

def hiking_conv_handler():
    conv_handler = ConversationHandler(
    entry_points=[CommandHandler('hiking', hiking_entrance)],
    states={
        HIKING_OPTIONS: [CallbackQueryHandler(hiking_options)],
        HIKING_READ: [MessageHandler(Filters.text, hiking_read)],
        HIKING_WRITE: [MessageHandler(Filters.all, hiking_write)],
        HIKING_READ_PHOTO: [CallbackQueryHandler(hiking_photo)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
    )
    return conv_handler 

def hiking_entrance(update, context):
    read_text = "Read hiking route / photo"
    write_text = "Share hiking route / photo"
    reply_markup = get_read_write_option(read_text, write_text, str(HIKING_READ), str(HIKING_WRITE))
    update.message.reply_text("Choose an option:", reply_markup=reply_markup)
    return HIKING_OPTIONS

def tvshow_read(update, context):
    global randomShows
    randomShows = get_tv_information()
    # print(randomShows)
    btnOptions = []
    for show in randomShows:
        btnOptions.append( [InlineKeyboardButton(
                text=show['title'], callback_data=show['link'])])
    btnOptions.append( [InlineKeyboardButton(
                text="Give me other tv shows", callback_data=0)])
    reply_keyboard_markup = InlineKeyboardMarkup(btnOptions)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Please select the TV Show", reply_markup=reply_keyboard_markup)
    # context.bot.send_message(chat_id=update.effective_chat.id, text=userSelectedTexts[1])
    return TVSHOW_READ_PHOTO

def tvshow_write(update, context):
    message = update.message
    if message is None:
        query = update.callback_query
        if query.data == str(TVSHOW_WRITE):
            context.bot.send_message(chat_id=update.effective_chat.id, 
                                        text='Please share the review of this tv show')
            return TVSHOW_WRITE
        elif query.data == str(TVSHOW_END):
            context.bot.send_message(chat_id=update.effective_chat.id, 
                                        text="Click /start to try again")
            return ConversationHandler.END
    elif message.text is not None:
        global tvReview
        tvshow_data = {
            "link" : tvReview["link"],
            "id" : message.chat.id,
            "review" : message.text
        }
        redis1.lpush("tvshow", json.dumps(tvshow_data))
        update.message.reply_text("Thank you for your share, Click /start to try again")
        return ConversationHandler.END
    else:
        update.message.reply_text("Your review is missing, please input again!")
   

def cancel(update, context):
    print('cancel invoke')
    ConversationHandler.END
    hiking_entrance(update, context)



def tv_show_conv_handler():
    conv_handler = ConversationHandler(
    entry_points=[CommandHandler('tvshow', tvshow_read)],
    states={
        TVSHOW_READ_PHOTO: [CallbackQueryHandler(tvshow_photo)],
        TVSHOW_WRITE_PROMPT: [CallbackQueryHandler(tvshow_write)],
        TVSHOW_WRITE: [MessageHandler(Filters.text, tvshow_write)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
    )
    return conv_handler


def welcome(update: Update, context: CallbackContext):
    welcome_message = '''Welcome,my friend, {}.
send /hiking to check or share hiking route and photos.
send /tvshow to read a TV show and write a review.
'''.format(
        update.message.from_user.first_name)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=welcome_message)
    #return ConversationHandler.END

def error_handler(update, context):
    logging.warning('Update "%s" caused error "%s"', update, context.error)
    context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, an error occurred.")

def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('If you want to use other function,send /welcome to explore.')

def main() -> None:
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    # updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    dispatcher = updater.dispatcher
    #default_handler = MessageHandler(Filters.all, welcome)
    
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command),equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)
    default_handler = MessageHandler(Filters.command, welcome)
    dispatcher.add_handler(CommandHandler("welcome", welcome))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(hiking_conv_handler())
    dispatcher.add_handler(tv_show_conv_handler())
    dispatcher.add_handler(default_handler)
    # dispatcher.add_error_handler(error_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
