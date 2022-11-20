import random
import re
import traceback
import database_funcs
import keyboards
import db_quiz

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
def write_msg(user_id, message, keyboard = ""):
    vk.method('messages.send', {'user_id': user_id, 'message': message, "random_id": 0, 'keyboard' : keyboard})

admin_id = 323359751
token = "d6b376a75c1a471d24aa4a62f87cbeb57747b4542b9b158a819e085fe95a5b6ba7c8d8e7c53702fd613e3"
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)
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
state = "default"
while True:
    try:

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:

                if event.to_me:
                    id = int(event.user_id)
                    request = event.text

                    if database_funcs.check_if_user_in_base(id) is None:
                        database_funcs.add_user_to_base(id)
                        write_msg(id, 'Привет! Теперь я знаю, кто ты такой и для тебя доступен весь мой функционал. Напиши "команды"!')

                    if request.lower() == "кто я":
                        name = database_funcs.get_user_nick(id)
                        ans = "Ты:" + " " + name + " " + "id:" " " + str(id)
                        write_msg(id, ans)

                    if request == "В меню":
                        state = "default"
                        write_msg(id, "Вы вернулись в меню", keyboards.menu)
                    elif "задание из егэ" in request.lower():
                        write_msg(id, "Какое именно задание?", keyboards.num_menu)
                        state = "choosing"

                    elif request.isdigit() and state == "choosing":
                        num = request
                        ans = database_funcs.get_task_by_num(request)
                        if ans != "Error":
                            write_msg(id, ans['text'])
                            database_funcs.update_user_last_asked_task(f"{num}:{ans['num']}", id)
                        else:
                            write_msg(id, messages['unclear_num'])

                        write_msg(id, "Нажми на кнопку, чтобы узнать решение и правильный ответ", keyboards.ege_menu)
                        state = "answering_t"
                    elif "вопрос с собеседования" in request.lower():
                        state = "net_or_py"
                        write_msg(id, "Какая тема?", keyboards.questions_menu)
                    elif state == "net_or_py" and request:
                        if request == "Вопросы по Python":
                            state = "answering_py"
                            q_id = db_quiz.get_last_asked_question(id, "asked_pyt_question")
                            if not q_id:
                                q_id = 1
                            else:
                                q_id += int(q_id) + 1
                            question = db_quiz.get_question(q_id, "python_questions")
                            db_quiz.update_user_last_asked_question(q_id, id, "asked_pyt_question")
                            write_msg(id, question[0], keyboards.create_vars_keyboard(question[1].split(";")))
                        elif request == "Вопросы по сетям":
                            state = "answering_net"
                            q_id = db_quiz.get_last_asked_question(id, "asked_net_question")
                            if not q_id:
                                q_id = 1
                            else:
                                q_id += int(q_id) + 1
                            question = db_quiz.get_question(q_id , "network_questions")
                            db_quiz.update_user_last_asked_question(q_id, id, "asked_net_question")
                            write_msg(id, question[0], keyboards.create_vars_keyboard(question[1].split(";")))
                    elif state == "answering_net":
                        q_id = int(db_quiz.get_last_asked_question(id, "asked_net_question"))
                        ra = db_quiz.get_question(q_id, "network_questions")[2]
                        if request == ra:
                            write_msg(id, "Молодец! Это правильный ответ")
                        else:
                            write_msg(id, "К сожалению, это неправильный ответ")
                            write_msg(id, f"Правильный ответ: {ra}")
                        state = "net_or_py"
                        write_msg(id, "Какая тема?", keyboards.questions_menu)
                    elif state == "answering_py":
                        q_id = int(db_quiz.get_last_asked_question(id, "asked_pyt_question"))
                        ra = db_quiz.get_question(q_id, "python_questions")[2]
                        if request == ra:
                            write_msg(id, "Молодец! Это правильный ответ")
                        else:
                            write_msg(id, "К сожалению, это неправильный ответ")
                            write_msg(id, f"Правильный ответ: {ra}")
                        state = "net_or_py"
                        write_msg(id, "Какая тема?", keyboards.questions_menu)


                    elif state == "answering_q":
                        id_task = database_funcs.get_task_id(id)
                        result = database_funcs.get_random_question_quiz(id_task)
                        vars = result['answers']
                        right_answer = result['right_answer']
                        if right_answer == request:
                            write_msg(id, "Правильно")
                        else:
                            write_msg(id, f"Правильный ответ: {right_answer}")
                        state = 'default'

                    elif state == "answering_t" and "решение" in request.lower():
                        sol = database_funcs.get_solution_to_user(id)
                        write_msg(id, sol)
                        write_msg(id, "Еще одно задание?", keyboards.num_menu)
                        state = "choosing"
                    elif request.lower() == "команды":
                        write_msg(id,"Я могу помочь тебе подготовиться как к ЕГЭ, так и к собеседованию", keyboards.menu)
                    elif "теория" in request.lower():
                        write_msg(id, "Теория к какому именно заданию вам нужна?", keyboards.num_menu)
                        state = "choosing_t"
                    elif state == "choosing_t" and request.isdigit():
                        num = request
                        if num.isdigit():
                            if 0 < int(num) < 28:
                                res = database_funcs.get_ege_theory(num)
                                write_msg(id, res)
                            else:
                                write_msg(id, messages['unclear_num'])
                        else:
                            write_msg(id, messages['unclear_num'])


                    elif "шутка" in request.lower() or "расскажи шутку" in request.lower() or "анекдот" in request.lower() or "расскажи анекдот" in request.lower():
                        res = database_funcs.get_random_joke()
                        write_msg(id, res)
                    elif "test" in request.lower() or "расскажи шутку" in request.lower() or "анекдот" in request.lower() or "расскажи анекдот" in request.lower():
                        res = database_funcs.get_random_question_quiz()
                        write_msg(id, res)

                    else:
                        write_msg(id, 'Я тебя не понимаю. Напиши "команды", чтобы узнать список доступных функций')
    except:

        write_msg(admin_id, "FatalError occured during runtime:" + "\n" + traceback.format_exc())
