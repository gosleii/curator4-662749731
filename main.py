import telebot
from telebot import types

bot = telebot.TeleBot('7022589359:AAHETz5bgUJ68hCZFE7qVpJSOl36kST-x1c')
# Список для хранения данных о пользователях
people = []


#####################################################################################
#           ОПИСАНИЕ СТРУКТУРЫ ДЛЯ ХРАНЕНИЯ ДАННЫХ О ПОЛЬЗОВАТЕЛЯХ                  #
#####################################################################################
class Person:
    def __init__(self, chat_id, user_state='', name='', surname='', age=0):
        self.chat_id = chat_id
        self.user_state = user_state
        self.name = name
        self.surname = surname
        self.age = age

    def update(self, **kwargs):
        self.user_state = kwargs.get('user_state', self.user_state)
        self.name = kwargs.get('name', self.name)
        self.surname = kwargs.get('surname', self.surname)
        self.age = kwargs.get('age', self.age)

    def print_data(self):
        print(f"Chat ID: {self.chat_id} User State: {self.user_state} Name: {self.name} Surname: {self.surname} Age: {self.age}")


def get_person(chat_id):
    for person in people:
        if person.chat_id == chat_id:
            return person
    return None

def add_person(chat_id):
    person = Person(chat_id)
    people.append(person)
    return person

def update_person(chat_id, **kwargs):
    person = get_person(chat_id)
    if person:
        person.update(**kwargs)

def print_people():
    print('Все пользователи:')
    for person in people:
        person.print_data()
    print('\n')

#####################################################################################
#                    БЛОК ОБРАБОТКИ КОМАНД                                          #
#####################################################################################

@bot.message_handler(commands=['start', 'help', 'prof', 'about'])
def handle_commands(message):
    chat_id = message.chat.id

    if message.text == '/start':
        text_start = 'Добро пожаловать, '

        if not get_person(chat_id):
            add_person(chat_id)
            text_start += 'кажется вы у нас впервые!\nЗаполните свои данные профиля нажав на "Изменить профиль"\n\n'
        else:
            text_start += f'{get_person(chat_id).name}!\n\n'
        update_person(chat_id, user_state='')

        text_start += "Используйте кнопки ниже:"
        bot.send_message(chat_id, text_start, reply_markup=get_navigation_buttons())
        print_people()

    elif message.text == '/help':
        update_person(chat_id, user_state='')
        bot.send_message(chat_id, "Хотел бы я помочь, но у меня лапки (", reply_markup=get_navigation_buttons())

    elif message.text == '/prof':
        update_person(chat_id, user_state='waiting_for_name')
        person = get_person(chat_id)

        text_prof = f'Ваш текущий профиль: \n\nИмя: {person.name}\nФамилия: {person.surname}\nВозраст: {person.age}'
        bot.send_message(chat_id, text=text_prof)

        remove_keyboard = types.ReplyKeyboardRemove()  # Скрываем кнопки
        bot.send_message(chat_id, "Можем изменить. Как вас зовут?", reply_markup=remove_keyboard)

    elif message.text == '/about':
        update_person(chat_id, user_state='')
        bot.send_message(
            chat_id,
            "Создатель этого чуда: @nipoks\\_kit 🐳\n"
            "Это мой первый тг бот на python🌚 Его изучал только для ЕГЭ с Викой 3 года назад\n\n"
            "Этой зимой был впервые написан бот рецептов блюд на *_JavaSpring_* с использованием *_PostgreSQL_*",
            parse_mode="MarkdownV2",
            reply_markup=get_navigation_buttons()
        )


#####################################################################################
#                 БЛОК ОБРАБОТКИ ПОЛУЧАЕМОГО ТЕКСТА                                 #
#####################################################################################

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    text = message.text

    if text in ['Помощь', 'О нас', 'На главную', 'Изменить профиль']:
        command_map = {
            'Помощь': '/help',
            'О нас': '/about',
            'На главную': '/start',
            'Изменить профиль': '/prof'
        }
        message.text = command_map[text]
        handle_commands(message)
        return

    person = get_person(chat_id)
    if person and person.user_state:
        if person.user_state == 'waiting_for_name':
            if len(text) > 20:
                bot.send_message(chat_id, 'Длина имени должна быть не более 20 символов.')
            else:
                update_person(chat_id, user_state='waiting_for_surname', name=text)
                bot.send_message(chat_id, 'Какая у вас фамилия?')

        elif person.user_state == 'waiting_for_surname':
            update_person(chat_id, user_state='waiting_for_age', surname=text)
            bot.send_message(chat_id, 'Сколько вам лет?')

        elif person.user_state == 'waiting_for_age':
            try:
                age = int(text)
                # в случае верного ввода пользователю отобразятся 2 кнопки: да нет
                # для подтверждения корректности введенных данных регистрации
                keyboard = types.InlineKeyboardMarkup()
                key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
                key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
                keyboard.add(key_yes, key_no)

                question = f'Ваш текущий профиль: \n\nИмя: {person.name}\nФамилия: {person.surname}\nВозраст: {age}'

                bot.send_message(chat_id, text=question, reply_markup=keyboard)
                update_person(chat_id, user_state='', age=age)

            except ValueError:
                bot.send_message(chat_id, 'Пожалуйста, введите число')
    else:
        bot.send_message(chat_id, 'Простите, я не знаю такой команды( Используйте кнопки ниже: ')

#####################################################################################
#               БЛОК ОБРАБОТКИ НАЖАТИЙ НА ИНЛАЙН-КНОПКИ                             #
#####################################################################################
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    chat_id = call.message.chat.id

    if call.data == 'yes':
        bot.send_message(chat_id, 'Запомню :)', reply_markup=get_navigation_buttons())
    elif call.data == 'no':
        update_person(chat_id, user_state='waiting_for_name')
        remove_keyboard = types.ReplyKeyboardRemove()  # Скрываем кнопки
        bot.send_message(chat_id, 'Давайте еще раз. Как вас зовут?', reply_markup=remove_keyboard)

#####################################################################################
#                      БЛОК КНОПОК НАВИГАЦИИ                                        #
#####################################################################################
def get_navigation_buttons():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_help = types.KeyboardButton('Помощь')
    button_about = types.KeyboardButton('О нас')
    button_start_reg = types.KeyboardButton('Изменить профиль')
    button_start = types.KeyboardButton('На главную')
    keyboard.add(button_help, button_about, button_start_reg, button_start)
    return keyboard



bot.polling(none_stop=True, interval=0)
