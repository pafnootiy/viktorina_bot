import os
import redis
import logging
import vk_api as vk
from dotenv import load_dotenv
from vk_api.exceptions import ApiError
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from questions_and_answers import get_question_answer, get_random_file


logger = logging.getLogger(__name__)


def init_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос',
                        color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)
    return keyboard


def send_messages(event, vk_api, message):
    keyboard = init_keyboard()
    vk_api.messages.send(
        peer_id=event.peer_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=message
    )


def get_random_question_and_answer(r, folder_with_files):
    random_question_and_answer = get_question_answer(
        get_random_file(folder_with_files))
    question = random_question_and_answer['question']
    answer = random_question_and_answer['answer']
    return question, answer


def ask_question(event, vk_api, r, folder_with_files):
    question, answer = get_random_question_and_answer(r, folder_with_files)
    r.set(f'question:{event.peer_id}', question)
    r.set(f'answer:{event.peer_id}', answer)
    message = question.replace("Вопрос \d:", "", 1)
    send_messages(event, vk_api, message)


def check_answer(event, vk_api, r):
    user_answer = r.get(f'answer:{event.peer_id}')
    if user_answer is not None and event.message.encode() in user_answer:
        message = "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        send_messages(event, vk_api, message)
    else:
        message = "Неверно, попробуй еще раз!"
        send_messages(event, vk_api, message)


def give_up(event, vk_api, r):
    user_answer = r.get(f'answer:{event.peer_id}')
    if user_answer is not None:
        message = f"Правильный ответ: {user_answer.decode('utf-8').replace('Ответ:', '')}"
        send_messages(event, vk_api, message)
    else:
        message = "Нет активного вопроса. Нажми «Новый вопрос», чтобы начать."
        send_messages(event, vk_api, message)


def main():
    load_dotenv()
    logging.basicConfig(filename='quiz.log', level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    VK_TOKEN = os.getenv("VK_TOKEN")
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PASS = os.getenv('REDIS_PASS')
    REDIS_PORT = os.getenv('REDIS_PORT')
    FILES = os.getenv("PATH_TO_FILE")
    vk_session = vk.VkApi(token=VK_TOKEN)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASS)

    for event in longpoll.listen():
        try:
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.message == 'Новый вопрос':
                    ask_question(event, vk_api, r, FILES)
                elif event.message == 'Сдаться':
                    give_up(event, vk_api, r)
                else:
                    check_answer(event, vk_api, r)
        except ApiError:
            logging.exception("Ошибка при работе с VK API")


if __name__ == '__main__':
    main()
