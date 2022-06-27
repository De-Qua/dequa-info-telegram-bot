import os
import requests
import subprocess as sp

from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext


load_dotenv()

TOKEN = os.getenv("TOKEN")
API_TOKEN = os.getenv("API_TOKEN")

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


def write_status(update: Update, context: CallbackContext) -> None:
    status = get_status()
    msg_status_list = [f"{GREEN_LIGHT if val else RED_LIGHT} \t {key.title()}" for key, val in status.items()]
    msg_status = '\n'.join(msg_status_list)
    msg = f"DeQua status:\n{msg_status}"

    update.message.reply_text(msg)
    return


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("status", write_status))

    # Start the Bot
    updater.start_polling()

    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
   main()
