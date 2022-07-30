import logging
import os
import requests
import telegram

from dotenv import load_dotenv
from time import sleep


def get_message_text(new_attempt):
    logging.basicConfig(level=logging.DEBUG)
    logging.warning('Сообщение составлено')

    message_title = f"Проверена работа «{new_attempt['lesson_title']}»\n{new_attempt['lesson_url']}\n\n"
    if new_attempt['is_negative']:
        return message_title + 'Предложены новые доработки.'
    else:
        return message_title + 'Работа принята!'


def main():
    load_dotenv()

    devman_url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': os.environ['DEVMAN_TOKEN'],
    }
    tg_token = os.environ['TELEGRAM_TOKEN']
    tg_chat_id = os.environ['TELEGRAM_CHAT_ID']
    bot = telegram.Bot(tg_token)

    while True:
        try:
            params = {}
            response = requests.get(devman_url, headers=headers, params=params)
            response.raise_for_status()
            rewiews = response.json()

            if rewiews['status'] == 'timeout':
                params['timestamp'] = rewiews['timestamp_to_request']
            elif rewiews['status'] == 'found':
                new_attempt = rewiews['new_attempts'][0]
                bot.send_message(chat_id=tg_chat_id, text=get_message_text(new_attempt))
                params['timestamp'] = new_attempt['timestamp']

        except requests.exceptions.ConnectionError:
            sleep(60)
            continue
        except requests.exceptions.ReadTimeout:
            continue


if __name__ == '__main__':
    main()
