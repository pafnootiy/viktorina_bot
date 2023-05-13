
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

logging.basicConfig(filename='quiz.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')


def init_keyboard():

    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос',
                        color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться',
                        color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет',
                        color=VkKeyboardColor.PRIMARY)

    return keyboard


def send_messages(event, vk_api, message):
    keyboard = init_keyboard()
    vk_api.messages.send(
        peer_id=event.peer_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=message
    )


def get_random_qustion_and_answer(redis_pass):
    folder_with_files = 'quiz_questions'

    r = redis.Redis(
        host='redis-12532.c284.us-east1-2.gce.cloud.redislabs.com',
        port=12532,
        password=redis_pass)

    random_qustion_and_answer = get_question_answer(
        get_random_file(folder_with_files))

    r.mset(
        {
            'question': random_qustion_and_answer['question'],
            'answer': random_qustion_and_answer['answer']
        }
    )

    user_question = r.get('question').decode(
        "utf-8").replace("Вопрос \d:", "", 1)
    user_answer = r.get('answer').decode("utf-8").replace('Ответ:\n', '')

    return user_question, user_answer


def ask_question(event, vk_api, redis_pass):
    user_question, user_answer = get_random_qustion_and_answer(redis_pass)
    message = user_question
    send_messages(event, vk_api, message)
    return user_question, user_answer


def check_answer(event, vk_api, user_answer):

    if event.message in user_answer:
        message = "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        send_messages(event, vk_api, message)
    else:
        message = "Неверно, попробуй еще раз!"
        send_messages(event, vk_api, message)


def giveup(event, vk_api, user_answer):

    message = f"Правильный ответ {user_answer}"
    send_messages(event, vk_api, message)


def main():

    load_dotenv()

    vk_token = os.getenv("VK_TOKEN")
    redis_pass = os.getenv("REDIS_PASS")
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    if event.text == 'Новый вопрос':
                        user_question, user_answer = ask_question(
                            event, vk_api, redis_pass)
                    elif event.message == 'Сдаться':
                        giveup(event, vk_api, user_answer)
                    else:
                        check_answer(event, vk_api, user_answer)

        except ApiError:
            logging.error(
                f"Ошибка при работе с VK API: {vk_api}")


if __name__ == '__main__':
    main()
