import logging
import os
import requests
import telegram

from dotenv import load_dotenv
from time import sleep


logger = logging.getLogger('TelegramHandler')


def get_message_text(new_attempt, logger):
    message_title = f"Проверена работа «{new_attempt['lesson_title']}»\n{new_attempt['lesson_url']}\n\n"
    logger.info('Составлено сообщение')
    if new_attempt['is_negative']:
        return message_title + 'Предложены новые доработки.'
    else:
        return message_title + 'Работа принята!'


def main():
    load_dotenv()

    admin_tg_token = os.environ['ADMIN_TELERGAM_TOKEN']
    admin_tg_chat_id = os.environ['ADMIN_TELEGRAM_CHAT_ID']
    admin_bot = telegram.Bot(admin_tg_token)

    class TelegramHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            admin_bot.send_message(chat_id=admin_tg_chat_id, text=log_entry)

    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramHandler())
    logger.info('Бот запущен')

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
            reviews = response.json()

            if reviews['status'] == 'timeout':
                params['timestamp'] = reviews['timestamp_to_request']
            elif reviews['status'] == 'found':
                new_attempt = reviews['new_attempts'][0]
                bot.send_message(chat_id=tg_chat_id, text=get_message_text(new_attempt))
                logger.info('Отправлено сообщение')
                params['timestamp'] = new_attempt['timestamp']
        except requests.exceptions.ConnectionError:
            sleep(60)
            continue
        except requests.exceptions.ReadTimeout:
            continue
        except Exception:
            logger.exception(Exception)


if __name__ == '__main__':
    main()
