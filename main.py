import os
import requests
import telegram

from dotenv import load_dotenv


def get_message_text(new_attempt):
    message_title = f"Проверена работа «{new_attempt['lesson_title']}»\n{new_attempt['lesson_url']}\n\n"
    if new_attempt['is_negative']:
        return message_title + 'Предложены новые доработки.'
    else:
        return message_title + 'Работа принята!'


def main():
    load_dotenv()

    devman_url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': os.getenv('DEVMAN_TOKEN'),
    }
    tg_token = os.getenv('TELEGRAM_TOKEN')
    tg_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    bot = telegram.Bot(tg_token)

    while True:
        try:
            response = requests.get(devman_url, headers=headers)
            response.raise_for_status()

            new_attempt = response.json()['new_attempts'][0]

            bot.send_message(chat_id=tg_chat_id, text=get_message_text(new_attempt))
            headers['timestamp'] = new_attempt['timestamp']

        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            continue


if __name__ == '__main__':
    main()
