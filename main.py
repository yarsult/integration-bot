from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import database_funcs

state = 0


messages = dict(commands="Задание хх - я отправлю тебе задание указанного номера (максимум - 27). Пример: задание 7 \n"
                         "\n"
                         "Решение - напиши эту команду, чтобы узнать ответ на задание, которое я отправил тебе \n"
                         "\n"
                         "Кто я - напиши, чтобы узнать информацию о себе \n"
                         "\n"
                         "Теория хх - напиши, чтобы получить теорию по указанному заданию (максимум - 27). Пример: теория 22 \n"
                         "\n"
                         '"Шутка" или "анекдот" - напиши, чтобы посмеяться)',
                unclear_num="Я не понимаю, какой номер ты имел в виду... Попробуй еще раз")


def main():
    updater = Updater('5331419578:AAGQUFsR7poil4NHuE34xAvQH9RQCoXIbU0', use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text, text))
    updater.start_polling()
    updater.idle()


def start(update, context):
    global id
    update.message.reply_text(messages['commands'])
    id = update.message.from_user.id
    if database_funcs.check_if_user_in_base(id) is None:
        database_funcs.add_user_to_base(id)
        update.message.reply_text('Привет! Теперь я знаю, кто ты такой и для тебя доступен весь мой функционал. \
                  Напиши "команды"!')


def whoami(update, context):
    global id
    name = database_funcs.get_user_nick(id)
    ans = "Ты:" + " " + name + " " + "id:" " " + str(id)
    update.message.reply_text(ans)


def task(update, context):
    global id
    num = update.message.text.split()[1]
    ans = database_funcs.get_task_by_num(num)
    if ans != "Error":
        update.message.reply_text(ans['text'])
        database_funcs.update_user_last_asked_task(num, ans['num'], id)
    else:
        update.message.reply_text(messages['unclear_num'])


def solution(update, context):
    global id
    sol = database_funcs.get_solution_to_user(id)
    update.message.reply_text(sol)


def theory(update, context):
    global id
    num = update.message.text.split()[1]
    if num.isdigit():
        if 0 < int(num) < 28:
            res = database_funcs.get_ege_theory(num)
            update.message.reply_text(res)
        else:
            update.message.reply_text(messages['unclear_num'])
    else:
        update.message.reply_text(messages['unclear_num'])


def fun(update, context):
    global id
    res = database_funcs.get_random_joke()
    update.message.reply_text(res)


def text(update, context):
    global state, markup
    req = update.message.text.lower()
    if req.split()[0] == 'задание':
        task(update, context)
    elif req == 'кто я':
        whoami(update, context)
    elif req == 'решение':
        solution(update, context)
    elif req == 'команды':
        update.message.reply_text(messages['commands'])
    elif req.split()[0] == 'теория':
        theory(update, context)
    elif 'шутк' in req or 'анекдот' in req:
        fun(update, context)
    else:
        update.message.reply_text('Я тебя не понимаю. Напиши "команды", чтобы узнать список доступных функций.')


if __name__ == '__main__':
    main()
