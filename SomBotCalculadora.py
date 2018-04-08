#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
Telegram bot that calculate a SomEnergia invoice

Usage:
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import config
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [['Dies de factura', 'Potencia'],
                  ['Consum en kWh', 'Lloguer comptador'],
                  ['Calcula']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{}: {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def start(bot, update):
    user_data = {}

    update.message.reply_text(
        "Calculdadora interactia de Som Energia. Completa les dades de la teva factura i et direm quan surt amb Som Energia. ",
        reply_markup=markup)

    return CHOOSING


def regular_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    update.message.reply_text(
            'Indica {}:'.format(text.lower()))

    return TYPING_REPLY


def received_information(bot, update, user_data):
    text = update.message.text
    print text
    try:
        numero = float(text)
    except ValueError:
        text = text.replace(",",".")
    finally:
        category = user_data['choice']
        user_data[category] = text
        del user_data['choice']

        update.message.reply_text("Dades entrades:"
                                  "{}".format(
                                      facts_to_str(user_data)), reply_markup=markup)
        return CHOOSING


def done(bot, update, user_data):
    if len(user_data) < 4:
        update.message.reply_text("Falten dades per calcular.",
            reply_markup=markup)
        return CHOOSING

    if 'choice' in user_data:
        del user_data['choice']
    logger.warning(user_data)
    result = 0
    
    dies = float(user_data['Dies de factura'])
    lloguerComptador = float(user_data['Lloguer comptador'])
    consum =  (float(user_data['Consum en kWh'])*0.130)
    print("Consum: %f" % consum)
    potencia =  round((float(user_data['Potencia']) * 38.043426 * dies / 365),2)
    print("Potencia %f " % potencia) 
    bosocial = round(float(dies*0.025),2)
    print("Bo social: %s" % bosocial)
    impost = round((lloguerComptador+consum+potencia)*0.0511269,2)
    print("Impost: %f" % impost)
    iva = round((lloguerComptador+consum+potencia+impost+bosocial) * 0.21,2) #IVA
    print("Iva: %f "%iva)

    result = consum + potencia + bosocial + impost + iva + lloguerComptador

    update.message.reply_text("Total factura amb Som Energia: "
                              "{}€\n\n"
                              "Per tornar a començar prem /start".format(round(result,2)))

    user_data.clear()
    return ConversationHandler.END

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.telegram['key'])

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [RegexHandler('^(Dies de factura|Potencia|Consum en kWh|Lloguer comptador)$',
                                    regular_choice,
                                    pass_user_data=True),
                       ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_information,
                                          pass_user_data=True),
                           ],
        },

        fallbacks=[RegexHandler('^Calcula$', done, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
