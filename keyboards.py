import sqlite3
import  vk_api
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType

def create_vars_keyboard(vars):
    res = VkKeyboard()
    res.add_button(label= vars[0], color="primary")
    for i in range (1, len(vars)):
        res.add_line()
        res.add_button(label = vars[i], color="primary")
    return res.get_keyboard()



menu = VkKeyboard()
menu.add_button(label = "Вопрос с собеседования", color = "primary")
menu.add_line()
menu.add_button(label = "Теория по ЕГЭ", color = "primary")
menu.add_button(label = "Шутка", color = "primary")
menu.add_line()
menu.add_button(label = "Задание из ЕГЭ", color = "primary")
menu = menu.get_keyboard()

questions_menu = VkKeyboard()
questions_menu.add_button(label="Вопросы по сетям", color= "primary")
questions_menu.add_line()
questions_menu.add_button(label="Вопросы по Python", color= "primary")
questions_menu.add_line()
questions_menu.add_button(label="В меню", color= "primary")
questions_menu = questions_menu.get_keyboard()

ege_menu = VkKeyboard()
ege_menu.add_button(label="Решение и правильный ответ", color="positive")
ege_menu.add_button(label="В меню", color="primary")
ege_menu = ege_menu.get_keyboard()
num_menu = VkKeyboard()
for i in range(1, 27 + 1):
    num_menu.add_button(label= i, color="primary")
    if i in [4, 8, 12, 16, 20, 24]:
        num_menu.add_line()

num_menu.add_button(label="В меню", color="secondary")



num_menu = num_menu.get_keyboard()
dmin_id = 323359751
token = "d6b376a75c1a471d24aa4a62f87cbeb57747b4542b9b158a819e085fe95a5b6ba7c8d8e7c53702fd613e3"
vk = vk_api.VkApi(token=token)
a = VkKeyboard()
a = a.get_keyboard()
longpoll = VkLongPoll(vk)
# def abc():
#     pass
# for event in longpoll.listen():
#             if event.type == VkEventType.MESSAGE_NEW:
#
#                 if event.to_me:
#                     id = int(event.user_id)
#                     request = event.text
#                     vk.method('messages.send', {'peer_id': id,
#                                                 'message': "test",
#                                                 'random_id': 0,
#                                                 'keyboard': menu})
