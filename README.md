# dequa-info-telegram-bot
Useful info bot for DeQua

## How to run it
The bot has just one main file python file and it is implemented with python-telegram-bot.

The required packages are listed in `env_dequa-telegram-bot.yml`

You should create a folder `env` and inside a yaml file `env.yml` where to put:
```
TOKEN: the_telegram_token_from_the_bot_father
API_TOKEN: the_token_to_access_dequa_api
WARNING_CHAT_IDS: [one_chat_id, another_chat_id]
INTERVAL_STATUS_CHECK: interval_time_in_seconds_to_check_the_status
```

Then you can just run the python script.

If you want to have it as a service it is recommended to put it on a server different from the main dequa server.

The program will check the status of the server every `INTERVAL_STATUS_CHECK` seconds (default 300s) and it will send a message to the chats in the yaml file if something is down!
