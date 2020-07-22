import os
import time
import requests
import telegram
from dotenv import load_dotenv
import logging


load_dotenv()
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
bot = telegram.Bot(token=TELEGRAM_TOKEN)
logging.basicConfig(
    filename='homework.log',
    format=f'%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)
logger = logging.getLogger(__name__)


def parse_homework_status(homework):
    error_msg = 'Не удалось получить статус или название домашней работы'
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if not homework_name or not homework_status:
        return error_msg
    if homework_status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif homework_status == 'approved':
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    else:  
        return error_msg  
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp=None):
    current_timestamp = current_timestamp or int(time.time())
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {
        'from_date': current_timestamp
    }
    try:
        homework_statuses = requests.get(API_URL, headers=headers, params=params)
    except requests.exceptions.RequestException as e:
        logging.exception(f'Обнаружена ошибка: {e}')

    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')  
            time.sleep(300)  

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
