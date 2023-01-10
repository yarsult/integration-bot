from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from random import choice
import database_funcs
import db_quiz
from secret import TOKEN

state = 0
reply_keyboard_main = [['Подготовка к ЕГЭ'], ['Вопросы собеседования по сетям'], ['Вопросы собеседования по Python']]
reply_keyboard_ege = [['Кто я', 'Задание'], ['Теория', 'Анекдот'], ['Команды', 'На главную']]
markup_main = ReplyKeyboardMarkup(reply_keyboard_main, one_time_keyboard=False)
markup_ege = ReplyKeyboardMarkup(reply_keyboard_ege, one_time_keyboard=False)
messages = dict(commands="Задание хх - я отправлю тебе задание указанного номера (максимум - 27). Пример: задание 7 \n"
                         "\n"
                         "Решение - напиши эту команду, чтобы узнать ответ на задание, которое я отправил тебе \n"
                         "\n"
                         "Кто я - напиши, чтобы узнать информацию о себе \n"
                         "\n"
                         "Теория хх - напиши, чтобы получить теорию по указанному заданию (максимум - 27). Пример: "
                         "теория 22 \n"
                         "\n"
                         '"Анекдот" - напиши, чтобы посмеяться)',
                initial="Я могу помочь с подготовкой к ЕГЭ по информатике или потренировать вас на вопросах "
                        "собеседования на it-специальность",
                unclear_num="Я не понимаю, какой номер ты имел в виду... Попробуй еще раз")


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text, text))
    updater.start_polling()
    updater.idle()


def start(update, context):
    global id, markup_main
    update.message.reply_text(messages['initial'], reply_markup=markup_main)
    id = update.message.from_user.id
    if database_funcs.check_if_user_in_base(id) is None:
        database_funcs.add_user_to_base(id)
        update.message.reply_text('Привет! Теперь я знаю, кто ты такой и для тебя доступен весь мой функционал. \
                  Напиши "команды"!')


def start_ege(update, context):
    global markup_ege
    update.message.reply_text(messages['commands'])
    update.message.reply_text('Приступим', reply_markup=markup_ege)


def whoami(update, context):
    name = update.message.chat.first_name
    ans = f'Вы пользователь Telegram {name}'
    update.message.reply_text(ans)


def task(update, context):
    global id
    num = update.message.text
    ans = database_funcs.get_task_by_num(num)
    group_keyboard = [['Решение', 'Выйти']]
    markup = ReplyKeyboardMarkup(group_keyboard, one_time_keyboard=True)
    if ans != "Error":
        update.message.reply_text(ans['text'], reply_markup=markup)
        database_funcs.update_user_last_asked_task(num, ans['num'], id)
    else:
        update.message.reply_text(messages['unclear_num'], reply_markup=markup)


def send_story(update, context):
    with open('stories.txt') as f:
        lst = f.read().split('sep')
    lst = list(filter(lambda x: x, lst))
    return choice(lst)


def solution(update, context):
    global id, markup_ege
    sol = database_funcs.get_solution_to_user(id)
    update.message.reply_text(sol, reply_markup=markup_ege)


def theory(update, context):
    global id, markup_ege
    num = update.message.text
    if num.isdigit():
        if 0 < int(num) < 28:
            res = database_funcs.get_ege_theory(num)
            update.message.reply_text(*res, reply_markup=markup_ege)
        else:
            update.message.reply_text(messages['unclear_num'], reply_markup=markup_ege)
    else:
        update.message.reply_text(messages['unclear_num'], reply_markup=markup_ege)


def fun(update, context):
    global id
    res = database_funcs.get_random_joke()
    update.message.reply_text(res)


def catch_task(update, context):
    global state
    reply_keyboard = [[str(i) for i in range(1, 10)], [str(i) for i in range(10, 19)], [str(i) for i in range(19, 28)]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text('Введите номер задания, с которым хотите ознакомиться', reply_markup=markup)
    state = 1


def catch_theory(update, context):
    global state
    reply_keyboard = [[str(i) for i in range(1, 10)], [str(i) for i in range(10, 19)], [str(i) for i in range(19, 28)]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text('Введите номер задания, с теорией по которыму хотите ознакомиться',
                              reply_markup=markup)
    state = 2


def net_question(update, context):
    global id, state, variants_net, right_ans_net, question_id_net
    if not db_quiz.get_last_asked_question(id, 'asked_net_question'):
        db_quiz.update_user_last_asked_question(0, id, 'asked_net_question')
    question_id_net = int(db_quiz.get_last_asked_question(id, 'asked_net_question')) + 1
    if question_id_net == 14:
        update.message.reply_text('Ты прошел все вопросы, вот тебе интересная история:')
        story = send_story(update, context)
        update.message.reply_text(story)
        db_quiz.update_user_last_asked_question(0, id, 'asked_net_question')
        enter_menu(update, context)
        return
    question, variants_net, right_ans_net = db_quiz.get_question(question_id_net, 'network_questions')
    reply_keyboard = [variants_net.split(';')[:2], variants_net.split(';')[2:], ['На главную']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(question, reply_markup=markup)
    state = 3


def pyt_question(update, context):
    global id, state, variants_pyt, right_ans_pyt, question_id_pyt
    if not db_quiz.get_last_asked_question(id, 'asked_pyt_question'):
        db_quiz.update_user_last_asked_question(0, id, 'asked_pyt_question')
    question_id_pyt = int(db_quiz.get_last_asked_question(id, 'asked_pyt_question')) + 1
    if question_id_pyt == 11:
        update.message.reply_text('Ты прошел все вопросы, вот тебе интересная история:')
        story = send_story(update, context)
        update.message.reply_text(story)
        db_quiz.update_user_last_asked_question(0, id, 'asked_net_question')
        enter_menu(update, context)
        return
    question, variants_pyt, right_ans_pyt = db_quiz.get_question(question_id_pyt, 'questions_quiz')
    reply_keyboard = [variants_pyt.split(';')[:2], variants_pyt.split(';')[2:], ['На главную']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(question, reply_markup=markup)
    state = 4


def enter_menu(update, context):
    global markup_main
    update.message.reply_text('Выберите дальнейшее действие',
                              reply_markup=markup_main)


def check_net_answer(update, context):
    global right_ans_net, id, question_id_net
    ans = update.message.text
    if ans == str(right_ans_net):
        update.message.reply_text('Ты прав')
    else:
        update.message.reply_text(f'Неверно, правильный ответ: {right_ans_net}')
    db_quiz.update_user_last_asked_question(question_id_net, id, 'asked_net_question')
    net_question(update, context)


def check_pyt_answer(update, context):
    global right_ans_pyt, id, question_id_pyt
    ans = update.message.text
    if ans == str(right_ans_pyt):
        update.message.reply_text('Ты прав')
    else:
        update.message.reply_text(f'Неверно, правильный ответ: {right_ans_pyt}')
    db_quiz.update_user_last_asked_question(question_id_pyt, id, 'asked_pyt_question')
    pyt_question(update, context)


def text(update, context):
    global state, markup_ege
    req = update.message.text.lower()
    if req == 'подготовка к егэ':
        start_ege(update, context)
    elif req == 'вопросы собеседования по сетям':
        net_question(update, context)
    elif req == 'вопросы собеседования по Python':
        pyt_question(update, context)
    elif req == 'задание':
        catch_task(update, context)
    elif req == 'кто я':
        whoami(update, context)
    elif req == 'решение':
        solution(update, context)
    elif req == 'команды':
        update.message.reply_text(messages['commands'])
    elif req.split()[0] == 'теория':
        catch_theory(update, context)
    elif 'шутк' in req or 'анекдот' in req:
        fun(update, context)
    elif state == 1 and req.isdigit():
        task(update, context)
    elif state == 2 and req.isdigit():
        theory(update, context)
    elif req == 'на главную':
        enter_menu(update, context)
    elif state == 3:
        check_net_answer(update, context)
    elif state == 4:
        check_pyt_answer(update, context)
    elif req == 'выйти':
        update.message.reply_text('Идём дальше', reply_markup=markup_ege)
    else:
        update.message.reply_text('Я тебя не понимаю. Напиши "команды", чтобы узнать список доступных функций.')


if __name__ == '__main__':
    main()