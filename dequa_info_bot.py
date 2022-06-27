import os
import requests
import subprocess as sp

import yaml

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext


SETTINGS_FILE = "env/env.yml"
DEFAULT_INTERVAL_STATUS_CHECK = 300

with open(SETTINGS_FILE, 'r') as stream:
    settings = yaml.load(stream, Loader=yaml.FullLoader)

TOKEN = settings["TOKEN"]
API_TOKEN = settings["API_TOKEN"]
WARNING_CHAT_IDS = settings["WARNING_CHAT_IDS"]
INTERVAL_STATUS_CHECK = settings.get("INTERVAL_STATUS_CHECK", DEFAULT_INTERVAL_STATUS_CHECK)

URL_TILES = "https://tiles.dequa.it/health"
URL_API = "https://api.dequa.it/api/system_info"
URL_SITE = "https://beta.dequa.it"
HEADER = {'Authorization': "Bearer " + API_TOKEN}

GREEN_LIGHT = "\U0001F7E2"
RED_LIGHT = "\U0001F534"


def ping(url: str) -> int:
    "Ping a website. Return a code: 0 means ping succesful."
    res = sp.call(['ping', '-c', '1', url],
                  stdout=sp.DEVNULL,
                  stderr=sp.DEVNULL
                  )
    return res


def status_server():
    "Check the status of the server"
    resp = ping('185.197.195.113')
    if resp == 0:
        return True
    else:
        return False


def status_site():
    "Get the status of the website"
    resp = requests.get(URL_SITE)
    if resp.status_code == 200:
        return True
    else:
        return False


def status_api():
    "Get the status of the backend"
    resp = requests.get(URL_API, headers=HEADER)
    if resp.status_code == 200:
        return True
    else:
        return False


def status_tiles():
    "Get the status of the tiles"
    resp = requests.get(URL_TILES)
    status = resp.status_code
    if status == 200:
        return True
    else:
        return False


def get_status() -> dict:
    "Get the status of the system"
    server = status_server()
    site = status_site()
    tiles = status_tiles()
    api = status_api()

    status = {
        "server": server,
        "site": site,
        "tiles": tiles,
        "api": api
    }

    return status


def warn_status(context: CallbackContext) -> None:
    status = get_status()
    if not all(status.values()):
        # everything is ok
        return
    else:
        msg_status_list = [f"{GREEN_LIGHT if val else RED_LIGHT} \t {key.title()}" for key, val in status.items()]
        msg_status = '\n'.join(msg_status_list)
        msg = f"Something is DOWN\n{msg_status}"
        for chat_id in WARNING_CHAT_IDS:
            context.bot.send_message(chat_id=chat_id, text=msg)


def write_status(update: Update, context: CallbackContext) -> None:
    status = get_status()
    msg_status_list = [f"{GREEN_LIGHT if val else RED_LIGHT} \t {key.title()}" for key, val in status.items()]
    msg_status = '\n'.join(msg_status_list)
    msg = f"DeQua status:\n{msg_status}"

    update.message.reply_text(msg)


def info_chat(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_message.chat_id
    update.message.reply_text(f"This is chat: {chat_id}")


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)
    jobs = updater.job_queue

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("status", write_status))
    dispatcher.add_handler(CommandHandler("chatinfo", info_chat))

    jobs.run_repeating(warn_status, interval=INTERVAL_STATUS_CHECK)

    # Start the Bot
    updater.start_polling()

    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
