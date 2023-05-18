import logging
import os
import redis


from telegram import Update, ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove
from questions_and_answers import QuizBot
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext


logger = logging.getLogger(__name__)

QUESTION, ANSWER, SCORE, CHECK_ANSWER, GIVE_UP = range(5)


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


def handle_new_question_request(update: Update, context: CallbackContext, FILES: str, r: redis.client.Redis) -> None:
    quiz_bot = QuizBot(FILES)
    random_question_and_answer = quiz_bot.get_random_question()
    r.mset(
        {
            'question': random_question_and_answer['question'],
            'answer': random_question_and_answer['answer']
        }
    )
    user_question = r.get('question').decode(
        "utf-8").replace("Вопрос \d:", "", 1)

    user_reply = update.message.text

    if user_reply == 'Новый вопрос':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=user_question,
                                 reply_markup=create_keyboard())

    return ANSWER


def handle_solution_attempt(update: Update, context: CallbackContext, r: redis.client.Redis) -> None:
    user_answer = r.get('answer').decode("utf-8").replace('Ответ:\n', '')
    user_reply = update.message.text

    if user_reply in user_answer:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»",
                                 reply_markup=create_keyboard())

        return QUESTION

    if user_reply == 'Сдаться':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Правильный ответ: {user_answer}",
            reply_markup=create_keyboard()
        )
        return QUESTION

    if user_reply not in ['Новый вопрос', 'Сдаться']:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Неправильно… Попробуйте ещё раз или нажмите «Сдаться»",
            reply_markup=create_keyboard()
        )

    return CHECK_ANSWER


def handle_give_up(update: Update, context: CallbackContext, r: redis.client.Redis) -> int:
    user_answer = r.get('answer').decode("utf-8").replace('Ответ:\n', '')
    print('test point')
    user_reply = update.message.text
    if user_reply == 'Сдаться':
        print('test point___1')
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Правильный ответ: {user_answer}",
            reply_markup=create_keyboard()
        )
        return QUESTION


def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Приятно было провести с тобой время, увидимся в следующий раз!',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main() -> None:
    load_dotenv()

    TOKEN = os.getenv('TG_API_TOKEN')
    FILES = os.getenv('PATH_TO_FILE')
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PASS = os.getenv('REDIS_PASS')
    REDIS_PORT = os.getenv('REDIS_PORT')
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASS)

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
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
            QUESTION: [
                MessageHandler(
                    Filters.regex('Новый вопрос'),
                    lambda update,
                    context: handle_new_question_request(
                        update, context, FILES, r)
                )
            ],
            ANSWER: [
                MessageHandler(Filters.regex('Сдаться'),
                               lambda update,
                               context: handle_give_up(update, context, r)
                               ),
                MessageHandler(Filters.text,
                               lambda update,
                               context: handle_solution_attempt(update, context, r))
            ],
            CHECK_ANSWER: [
                MessageHandler(Filters.text,
                               lambda update, context: handle_solution_attempt(update, context, r))
            ],
            GIVE_UP: [
                MessageHandler(Filters.regex('Сдаться'),
                               lambda update, context: handle_give_up(update, context, r))
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
