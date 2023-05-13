import logging
import os
import redis
import telegram

from telegram import Update, ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove
from questions_and_answers import get_question_answer, get_random_file
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


load_dotenv()


QUESTION, ANSWER, SCORE = range(3)
TOKEN = os.getenv('TG_API_TOKEN')
CHAT_ID = os.getenv('TG_CHAT_ID')
FILES = 'quiz_questions'

# r = redis.Redis(
#     host='redis-12532.c284.us-east1-2.gce.cloud.redislabs.com',
#     port=12532,
#     password=os.getenv("REDIS_PASS"))
# r = 'redis://pafnootiy86@gmail.com:Joke4elgin6@@redis-12532.c284.us-east1-2.gce.cloud.redislabs.com:12532'

r = redis.Redis(
  host='redis-12532.c284.us-east1-2.gce.cloud.redislabs.com',
  port=12532,
  password=os.getenv('REDIS_PASS'))
 

def create_keyboard():
    custom_keyboard = [['Новый вопрос',
                        'Сдаться'], ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)

    return reply_markup


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Привет {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )
    update.message.reply_text(
        '''Добро пожаловать в Викторину! \nДля начала игры нажми на кнопку " Новый вопрос"
         ''',
        reply_markup=create_keyboard())

    return QUESTION


def handle_new_question_request(update: Update, context: CallbackContext) -> None:
    random_qustion_and_answer = get_question_answer(
        get_random_file(FILES))

    r.mset(
        {
            'question': random_qustion_and_answer['question'],
            'answer': random_qustion_and_answer['answer']
        }
    )
    user_question = r.get('question').decode(
        "utf-8").replace("Вопрос \d:", "", 1)

    bot = telegram.Bot(token=TOKEN)
    user_reply = update.message.text

    if user_reply == 'Новый вопрос':
        bot.send_message(chat_id=CHAT_ID,
                         text=user_question,
                         reply_markup=create_keyboard())

    return ANSWER


def handle_solution_attempt(update: Update, context: CallbackContext) -> None:
    bot = telegram.Bot(token=TOKEN)
    user_answer = r.get('answer').decode("utf-8").replace('Ответ:\n', '')
    user_reply = update.message.text

    if user_reply in user_answer:
        bot.send_message(chat_id=CHAT_ID,
                         text="Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»",
                         reply_markup=create_keyboard())

        return QUESTION

    if user_reply not in user_answer and user_reply not in ['Новый вопрос', 'Сдаться']:
        bot.send_message(chat_id=CHAT_ID,
                         text="Неправильно… Попробуешь ещё раз?",
                         reply_markup=create_keyboard())

    if user_reply == 'Сдаться':
        bot.send_message(chat_id=CHAT_ID,
                         text=f'Привильный ответ : {user_answer}',
                         reply_markup=create_keyboard())

        return QUESTION


def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Приятно было провести с тобой время, увидимся в следующий раз!',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main() -> None:
    file_handler = logging.FileHandler('bot.log')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION: [MessageHandler(Filters.regex('Новый вопрос'), handle_new_question_request)],
            ANSWER: [MessageHandler(Filters.text, handle_solution_attempt)],

        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
