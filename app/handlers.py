import random

import emoji
import asyncio
from asyncio import sleep

from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery, InputFile
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.callback_data import CallbackData

from yoomoney import Client, Quickpay

from main import bot, dp, db

from config import admin_id, gallows_stages, slovar, YOOMONEY_TOKEN, YOOMONEY_WALLET

'''ОТКРЫТИЕ СЛОВАРЯ ДЛЯ ВИСЕЛИЦЫ'''

f = open('slova.txt', 'r', encoding='cp1251')
words = []
for word in f:
    words.append(word)
f.close()

'''СОСТОЯНИЯ ПОЛЬЗОВАТЕЛЯ'''


class Modes(StatesGroup):
    BaC_mode = State()
    Gallows_mode = State()
    String_len = State()
    Numbers_war_mode = State()
    NumwarsMP = State()
    GetInfo = State()
    Donation = State()
    Event = State()

'''КНОПКА НАЗАД'''
markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, selective=True, one_time_keyboard=True)
back_button = KeyboardButton(text="/back")
markup.add(back_button)

'''ЗНАЧОК ДОНАТЕРА'''
donater = emoji.emojize(":moneybag:", language='alias')

'''КЛАССЫ CALLBACK, СЛОВАРЬ ДЛЯ NumwarsMP'''
NWMPCreateGameData = CallbackData("new_game", "creator")
FutureOpponent = CallbackData("opponent", "creator", "opponent_id", "opponent_name")
NWMPGame = CallbackData("pos", "current_turn", "str_pos")
NWMPRecreateGame = CallbackData("recreate_game", "answer", "p1", "p2", "message")
Opponents = {}
TextsForRecreating = {}

'''СООБЩЕНИЕ АДМИНУ ПРИ ЗАПУСКЕ'''


async def send_to_admin(dp):
    await bot.send_message(chat_id=admin_id, text="Бот запущен")


'''ПОВЫШЕНИЕ УРОВНЯ'''


def lvl_up(user, exp):
    db.update_info(user, 'exp', db.get_info(user, 'exp') + exp)
    if db.get_info(user, 'exp') >= 100:
        db.update_info(user, 'lvl', db.get_info(user, 'lvl') + 1)
        db.update_info(user, 'exp', db.get_info(user, 'exp') - 100)


'''ВЫСТАВЛЕНИЕ ПЛАТЕЖА, ПРОВЕРКА ПЛАТЕЖА'''


async def payment(user):
    current_payment_status = db.get_info(user, 'payment_status')

    if current_payment_status == '0' or not current_payment_status:
        quickpay = Quickpay(
            receiver=YOOMONEY_WALLET,
            quickpay_form="shop",
            targets="Разблокировка функционала бота",
            paymentType="SB",
            sum=3,
            label=str(user)
        )
        db.update_info(user, 'payment_status', quickpay.label)
    else:
        quickpay = Quickpay(
            receiver="YOOMONEY_WALLET",
            quickpay_form="shop",
            targets="Разблокировка функционала бота",
            paymentType="SB",
            sum=3,
            label=current_payment_status
        )

    pay_button = InlineKeyboardButton(text='Купить', url=quickpay.redirected_url)
    money_keyboard = InlineKeyboardMarkup(row_width=1)
    money_keyboard.insert(pay_button)

    await bot.send_message(
        user,
        f'Вы можете разблокировать весь функционал бота всего за 3 рубля!\n'
        f'Если после оплаты ничего не произошло, писать <a href="tg://user?id={admin_id}">сюда</a>.',
        reply_markup=money_keyboard
    )

    await sleep(600)
    check_payment(user)


def check_payment(user):
    if db.get_info(user, 'payment_status') != '0':
        if db.get_info(user, 'donate_status') == 1:
            return True
        client = Client(YOOMONEY_TOKEN)
        history = client.operation_history(label=db.get_info(user, 'payment_status'))
        for operation in history.operations:
            if operation.status == 'success':
                db.update_info(user, 'donate_status', 1)
                db.update_info(user, 'payment_status', '0')
                asyncio.run(send_database())
                return True
    return False


'''СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ В БД'''


def create_user(message, user):
    real_name = message.from_user.full_name
    username = ""
    for i in range(len(real_name)):
        if real_name[i] in slovar:
            username += real_name[i]
    url = f'<a href="tg://user?id={user}">{username}</a>'
    db.add_user(user, url)


'''КОМАНДЫ START И HELP'''


@dp.message_handler(commands='start', chat_type='private')
async def start(message: Message):
    user = message.from_user.id
    if not db.user_exists(user):
        create_user(message, user)
    text = f'Привет, {message.from_user.full_name}. Давай начнём общение! Напиши мне "/help" для ' \
           f'получения информации обо мне.'
    await message.answer(text=text)


@dp.message_handler(commands='help')
async def help(message: Message):
    await message.answer(text=f"Мои команды:\n"
                              f"\n"
                              f"Общие:\n"
                              f"\"/help\" - вызывает эти сообщения\n"
                              f"\"/BaC\" - запускает игру \"Быки и коровы\"\n"
                              f"\"/gallows\" - запускает игру \"Виселица\"\n"
                              f"\"/numwars\" - запускает игру \"Цифровые войны\"\n"
                              f"\"/setstrlen\" - Установка длины строки в \"Цифровых войнах\"\n"
                              f"\"/back\" - возвращает к выбору режима работы\n"
                              f"\"/lvl\" - показывает ваш уровень\n"
                              f"\n"
                              f"Только в чате с ботом:\n"
                              f"\"/start\" - начало общения\n"
                              f"\"/top\" - выводит топ 10 пользователей по уровню\n"
                              f"\"/editname\" - преображает ваше имя в топе\n"
                              f"\"/NWMP_top\" - выводит топ 10 игроков по победам в NumwarsMP, "
                              f"их победы(W), поражения(L) и процент побед(%)\n"
                              f"\n"
                              f"Только в чате группы:\n"
                              f"\"/NWMPCreate\" - создаёт игру \"Цифровые войны MP\"\n"
                              f"\"/NWMPQuit\" - удаляет игру \"Цифровые войны MP\"\n"
                              f"\"/numwarsMP\" - включает или выключает игру \"Цифровые войны MP\"")
    await message.answer(text=f"Мои игры:\n"
                              f"\n\n"
                              f"1) Быки и коровы:\n"
                              f"\n"
                              f"В игре \"Быки и коровы\" бот загадывает вам четырёхзначное число "
                              f"без повторяющихся цифр, которое может начинаться с нуля. "
                              f"Вы должны написать ему своё четырёхзначное число. "
                              f"Тогда он ответит вам, сколько в вашем числе быков и коров. "
                              f"Если количество быков будет равно 4, то вы угадали число."
                              f"\n\n\n"
                              f"2) Виселица:\n"
                              f"\n"
                              f"В игре \"Виселица\" бот загадывает вам слово и выводит "
                              f"количество букв в слове. Вы должны писать ему по одной букве, "
                              f"чтобы угадать слово. За 9 неправильных букв вы проигрываете."
                              f"\n\n\n"
                              f"3) Цифровые войны:\n"
                              f"\n"
                              f"В начале игры \"Цифровые войны\" бот генерирует строку заданной вами "
                              f"длины, состоящую из случайных цифр. За каждый ход вы можете написать "
                              f"номер цифры в строке, чтобы уменьшить её на 1. Если вы захотите уменьшить 0, "
                              f"то он сотрётся, и сотрутся все цифры справа от него. Тот, кто полностью "
                              f"стирает строку, проигрывает. Изменить длину строки можно командой "
                              f"\"/setstrlen\"."
                              f"\n\n\n"
                              f"4) Цифровые войны MP:\n"
                              f"\n"
                              f"Это \"Цифровые войны\", но для двоих. Необходимо создать группу с "
                              f"другим игрококм и ботом.")
    await message.answer(text=f"Система уровней:\n\n"
                              f"Посмотреть свой уровень можно командой \"/lvl\".\n"
                              f"1 уровень - 100 очков опыта\n"
                              f"Очки опыта за игры:\n"
                              f"Быки и коровы - 40\n"
                              f"Виселица - 40\n"
                              f"Цифровые войны - 40\n"
                              f"Цифровые войны MP - 90\n"
                              f"За достижение 20 уровня можно бесплатно разблокировать"
                              f" команды \"/top\" и \"/NWMP_top\".")


@dp.message_handler(commands='lvl')
async def lvl(message: Message):
    user = message.from_user.id
    if not db.user_exists(user):
        create_user(message, user)
        await message.answer(text="Вас не было в списке пользователей бота, но сейчас это было исправлено. "
                                  "Повторите попытку")
    else:
        await message.answer(text=f"Уровень: {db.get_info(user, 'lvl')}.\n"
                                  f"Опыта до следующего уровня: {100 - db.get_info(user, 'exp')}.")


@dp.message_handler(state=Modes.all_states_names, commands='back')
@dp.message_handler(Text(equals='back', ignore_case=True), state=Modes.all_states_names)
async def back(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == Modes.BaC_mode.state:
        await message.answer(text=f"Игра \"Быки и коровы\" выключена.", reply_markup=ReplyKeyboardRemove())
        await state.finish()
    elif current_state == Modes.Gallows_mode.state:
        await message.answer(text=f"Игра \"Виселица\" выключена.", reply_markup=ReplyKeyboardRemove())
        await state.finish()
    elif current_state == Modes.Numbers_war_mode.state:
        await message.answer(text=f"Игра \"Цифровые войны\" выключена.", reply_markup=ReplyKeyboardRemove())
        await state.finish()
    elif current_state == Modes.String_len.state:
        await message.reply(text=f"Изменения отменены.", reply_markup=markup)
        await Modes.Numbers_war_mode.set()


@dp.message_handler(commands='BaC', chat_type='private')
@dp.message_handler(Text(equals='BaC', ignore_case=True), chat_type='private')
async def BaC(message: Message):
    user = message.from_user.id
    if not db.user_exists(user):
        create_user(message, user)
        await message.answer(text="Вас не было в списке пользователей бота, но сейчас это было исправлено. "
                                  "Повторите попытку")
    else:
        await Modes.BaC_mode.set()
        await message.reply(text=f"Игра \"Быки и коровы\" запущена.", reply_markup=markup)
        numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        if db.get_info(user, 'BaC_number') == '0000':
            db.update_info(user, 'BaC_number', ''.join(random.sample(numbers, 4)))
            await message.answer(text=f"Число загадано!")


@dp.message_handler(commands='gallows', chat_type='private')
@dp.message_handler(Text(equals='gallows', ignore_case=True), chat_type='private')
async def gallows(message: Message):
    user = message.from_user.id
    if not db.user_exists(user):
        create_user(message, user)
        await message.answer(text="Вас не было в списке пользователей бота, но сейчас это было исправлено. "
                                  "Повторите попытку")
    else:
        await Modes.Gallows_mode.set()
        await message.reply(text=f"Игра \"Виселица\" запущена.", reply_markup=markup)
        if db.get_info(user, 'gallows_word') == '':
            gallows_word = random.choice(words)
            gallows_word = gallows_word.strip()
            db.update_info(user, 'gallows_word', gallows_word)
            db.update_info(user, 'users_word', '_' * len(gallows_word))
            await message.answer(text=f"Слово загадано! Количество букв: {len(gallows_word)}.")
        else:
            users_word = db.get_info(user, 'users_word')
            users_attempts = db.get_info(user, 'users_attempts')
            users_faults = db.get_info(user, 'users_faults')
            good_attempts = '|'
            wrong_attempts = ''
            for j in range(len(users_word)):
                good_attempts = good_attempts + users_word[j] + '|'
            for k in range(len(users_attempts)):
                wrong_attempts = wrong_attempts + users_attempts[k] + '  '
            await message.reply(text=f"{good_attempts}\n"
                                     f"{gallows_stages[users_faults]}\n"
                                     f"{wrong_attempts}", reply_markup=markup)


@dp.message_handler(commands='numwars', chat_type='private')
@dp.message_handler(Text(equals='numwars', ignore_case=True), chat_type='private')
async def numwars(message: Message):
    user = message.from_user.id
    if not db.user_exists(user):
        create_user(message, user)
        await message.answer(text="Вас не было в списке пользователей бота, но сейчас это было исправлено. "
                                  "Повторите попытку")
    else:
        await message.reply(text=f"Игра \"Цифровые войны\" запущена.", reply_markup=markup)
        if db.get_info(user, 'str_length') == -1:
            await message.answer(text=f"Задайте длину строки от 5 до 30.")
            await Modes.String_len.set()
        else:
            await message.answer(text=f"{db.get_info(user, 'string_of_numbers')}")
            await message.answer(text=f"Ваш ход!")
            await Modes.Numbers_war_mode.set()


@dp.message_handler(state=Modes.Numbers_war_mode, commands='setstrlen')
@dp.message_handler(Text(equals='setstrlen', ignore_case=True), state=Modes.Numbers_war_mode)
async def setstrlen(message: Message):
    user = message.from_user.id
    if not db.user_exists(user):
        create_user(message, user)
        await message.answer(text="Вас не было в списке пользователей бота, но сейчас это было исправлено. "
                                  "Повторите попытку")
    else:
        await message.reply(text=f"Задайте длину строки от 5 до 30.", reply_markup=markup)
        await Modes.String_len.set()


@dp.message_handler(state=Modes.String_len, content_types=['text'])
async def Modes_String_len(message: Message):
    numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    user = message.from_user.id
    if 5 <= int(message.text) <= 30:
        db.update_info(user, 'str_length', int(message.text))
        await message.reply(text=f"Изменения успешно сохранены.", reply_markup=markup)
        if db.get_info(user, 'string_of_numbers') == '':
            string_of_numbers = ''.join(random.choice(numbers) for i in range(int(message.text)))
            db.update_info(user, 'string_of_numbers', string_of_numbers)
            await message.answer(text=f"{string_of_numbers}")
            await message.answer(text=f"Ваш ход!")
        else:
            await message.answer(text=f"{db.get_info(user, 'string_of_numbers')}")
            await message.answer(text=f"Ваш ход!")
        await Modes.Numbers_war_mode.set()
    else:
        await message.reply(text=f"Некорректный ввод!", reply_markup=markup)


@dp.message_handler(state=Modes.BaC_mode, content_types=['text'])
async def Modes_BaC_mode(message: Message):
    user = message.from_user.id
    msg = message.text
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    if len(msg) == 4:
        for x in msg:
            if x not in numbers or msg.count(x) != 1:
                await message.reply(text=f"Некорректный ввод!", reply_markup=markup)
                break
        else:
            a = db.get_info(user, 'BaC_number')
            b = msg
            bulls = 0
            cows = 0
            for x in range(4):
                for y in range(4):
                    if a[x] == b[y] and x == y:
                        bulls += 1
                    if a[x] == b[y] and x != y:
                        cows += 1
            db.update_info(user, 'BaC_attempts', db.get_info(user, 'BaC_attempts') + 1)
            if bulls < 4:
                await message.reply(text=f"{bulls}Б {cows}К", reply_markup=markup)
            else:
                lvl_up(user, 40)
                await message.answer(text=f"Поздравляю! Это правильное число!"
                                          f" Вам потребовалось всего попыток: {db.get_info(user, 'BaC_attempts')}!")
                db.update_info(user, 'BaC_attempts', 0)
                new_number = ''.join(random.sample(numbers, 4))
                db.update_info(user, 'BaC_number', new_number)
                await message.reply(text=f"Новое число загадано!", reply_markup=markup)
    else:
        await message.reply(text=f"Некорректный ввод!", reply_markup=markup)


@dp.message_handler(state=Modes.Gallows_mode, content_types=['text'])
async def Modes_Gallows_mode(message: Message):
    symbols = ['А', 'Б', 'В', 'Г', 'Д', 'Е', chr(203), chr(1025), 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р',
               'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я']
    good_attempts = '|'
    wrong_attempts = ''
    user = message.from_user.id
    msg = message.text
    try:
        msg = msg.upper()
    except:
        await message.reply(text=f"Некорректный ввод!", reply_markup=markup)
    else:
        gallows_word = db.get_info(user, 'gallows_word')
        users_word = db.get_info(user, 'users_word')
        users_attempts = db.get_info(user, 'users_attempts')
        users_faults = db.get_info(user, 'users_faults')
        if len(msg) == 1 and msg not in users_attempts and msg not in users_word and msg in symbols:
            if msg in gallows_word:
                for i in range(len(gallows_word)):
                    if msg == gallows_word[i]:
                        users_word = users_word[:i] + msg + users_word[i + 1:]
                        db.update_info(user, 'users_word', users_word)
            else:
                users_faults += 1
                db.update_info(user, 'users_faults', users_faults)
                users_attempts = users_attempts + msg
                db.update_info(user, 'users_attempts', users_attempts)
            for j in range(len(users_word)):
                good_attempts = good_attempts + users_word[j] + '|'
            for k in range(len(users_attempts)):
                wrong_attempts = wrong_attempts + users_attempts[k] + '  '
            await message.reply(text=f"{good_attempts}\n"
                                     f"{gallows_stages[users_faults]}\n"
                                     f"{wrong_attempts}", reply_markup=markup)
            if gallows_word == users_word:
                lvl_up(user, 40)
                await message.answer(text=f"Поздравляю! Вы отгадали слово \"{gallows_word}\".")
                gallows_word = random.choice(words)
                gallows_word = gallows_word.strip()
                db.update_info(user, 'gallows_word', gallows_word)
                users_word = '_' * len(gallows_word)
                db.update_info(user, 'users_word', users_word)
                users_attempts = ''
                db.update_info(user, 'users_attempts', users_attempts)
                users_faults = 0
                db.update_info(user, 'users_faults', users_faults)
                await message.reply(text=f"Новое слово загадано! Количество букв: {len(gallows_word)}.",
                                    reply_markup=markup)
            if users_faults == 9:
                await message.answer(text=f"Вы проиграли! Было загадано слово \"{gallows_word}\".")
                gallows_word = random.choice(words)
                gallows_word = gallows_word.strip()
                db.update_info(user, 'gallows_word', gallows_word)
                users_word = '_' * len(gallows_word)
                db.update_info(user, 'users_word', users_word)
                users_attempts = ''
                db.update_info(user, 'users_attempts', users_attempts)
                users_faults = 0
                db.update_info(user, 'users_faults', users_faults)
                await message.reply(text=f"Новое слово загадано! Количество букв: {len(gallows_word)}.",
                                    reply_markup=markup)
        else:
            await message.reply(text=f"Некорректный ввод!", reply_markup=markup)


@dp.message_handler(state=Modes.Numbers_war_mode, content_types=['text'])
async def Modes_Numbers_war_mode(message: Message):
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    user = message.from_user.id
    str_len = db.get_info(user, 'str_length')
    string_of_numbers = db.get_info(user, 'string_of_numbers')
    for num in message.text:
        if num not in numbers:
            await message.reply(text=f"Некорректный ввод!", reply_markup=markup)
            break
    else:
        n = int(message.text)
        if 0 < n <= len(string_of_numbers):
            s = string_of_numbers
            if int(s[n - 1]) > 0:
                s = s[:n - 1] + str(int(s[n - 1]) - 1) + s[n:]
            else:
                s = s[:n - 1]
            if s == '':
                await message.answer(text=f"Вы проиграли.")
                string_of_numbers = ''.join(random.choice(numbers) for i in range(str_len))
                db.update_info(user, 'string_of_numbers', string_of_numbers)
                await message.answer(text=f"{string_of_numbers}")
                await message.reply(text=f"Ваш ход!", reply_markup=markup)
            else:
                await message.reply(text=f"{s} Мой ход.", reply_markup=markup)
                if s == '0':
                    lvl_up(user, 40)
                    await message.answer(text=f"Я проиграл.")
                    string_of_numbers = ''.join(random.choice(numbers) for i in range(str_len))
                    db.update_info(user, 'string_of_numbers', string_of_numbers)
                    await message.answer(text=f"{string_of_numbers}")
                    await message.reply(text=f"Ваш ход!", reply_markup=markup)
                else:
                    for o in range(1, len(s)):
                        if (s[o] == "0") and ((sum(map(int, s[:o])) + len(s[:o])) % 2 == 1) and (s[o - 1] != "0"):
                            s = s[:o - 1] + str(int(s[o - 1]) - 1) + s[o:]
                            db.update_info(user, 'string_of_numbers', s)
                            await message.reply(text=f"{s} Ваш ход!", reply_markup=markup)
                            break
                    else:
                        solution = -1
                        turns = 0
                        for j in range(len(s)):
                            turns += int(s[j]) + 1
                            if ((turns % 2) == 1) and (j != (len(s) - 1)):
                                solution = j + 1
                                if (s[solution] == "1") and (solution != (len(s) - 1)):
                                    continue
                                break
                            if ((turns % 2) == 0) and (j == len(s) - 1):
                                solution = j
                        if solution != -1:
                            if int(s[solution]) > 0:
                                s = s[:solution] + str(int(s[solution]) - 1) + s[solution + 1:]
                            elif int(s[solution]) == 0:
                                s = s[:solution]
                            db.update_info(user, 'string_of_numbers', s)
                            await message.reply(text=f"{s} Ваш ход!", reply_markup=markup)
                        else:
                            for k in range(len(s)):
                                if int(s[k]) > 0 and k == 0:
                                    s = str(int(s[k]) - 1) + s[k + 1:]
                                    break
                                elif k == 1 and int(s[k]) > 1:
                                    s = s[:k] + str(int(s[k]) - 1) + s[k + 1:]
                                    break
                                elif k > 1 and int(s[k]) > 0:
                                    s = s[:k] + str(int(s[k]) - 1) + s[k + 1:]
                                    break
                                elif k > 1 and int(s[k]) == 0:
                                    s = s[:k]
                                    break
                            db.update_info(user, 'string_of_numbers', s)
                            await message.reply(text=f"{s} Ваш ход!", reply_markup=markup)
        else:
            await message.reply(text=f"Некорректный ввод!", reply_markup=markup)


@dp.message_handler(commands='top', chat_type='private')
async def top(message: Message):
    user = message.from_user.id
    donate_status = db.get_info(user, 'donate_status')
    check_result = False
    if (donate_status != 1 and db.get_info(user, 'payment_status') != '0') or (db.get_info(user, 'lvl') >= 20):
        check_result = check_payment(user)
    if donate_status == 1 or db.get_info(user, 'lvl') >= 20 or check_result:
        Data = db.rating()
        leaderboard = ''
        id_exp = {}
        id_url = {}
        place = 0
        for k in range(len(Data)):
            id_exp[Data[k][0]] = Data[k][3] * 100 + Data[k][2]
            id_url[Data[k][0]] = Data[k][1]
        sorted_users = dict(sorted(id_exp.items(), key=lambda x: x[1], reverse=True))
        for leader in sorted_users.keys():
            place += 1
            leaderboard = leaderboard + f"{place}) {id_url[leader]} Опыт: {sorted_users[leader]}\n"
            if place == 10:
                break
        await message.answer(text=leaderboard)
    else:
        await message.answer(text="Функция заблокирована!")
        await payment(user)


@dp.message_handler(commands='editname', chat_type='private')
async def editname(message: Message):
    user = message.from_user.id
    donate_status = db.get_info(user, 'donate_status')
    check_result = False
    if donate_status != 1 and db.get_info(user, 'payment_status') != '0':
        check_result = check_payment(user)
    if donate_status == 1 or check_result:
        if user != admin_id:
            db.update_info(user, 'url',
                           f'<a href="tg://user?id={user}">{donater}{message.from_user.full_name}{donater}</a>')
            await message.answer(text="Имя успешно изменено!")
    else:
        await message.answer(text="Функция заблокирована!")
        await payment(user)


@dp.message_handler(chat_type='group', commands='NWMPCreate')
@dp.message_handler(Text(equals='NWMPCreate', ignore_case=True), chat_type='group')
async def NWMPCreateGame(message: Message):
    if (message.from_user.id not in Opponents.keys()) and (not db.game_exists(message.from_user.id)):
        join_game = InlineKeyboardButton(text="Присоединиться",
                                         callback_data=NWMPCreateGameData.new(creator=message.from_user.id))
        GameCreation = InlineKeyboardMarkup(row_width=1)
        GameCreation.insert(join_game)
        Opponents[message.from_user.id] = []
        game_creation = await message.answer(
            text=f'Нажмите, чтобы сыграть в цифровые войны с {message.from_user.full_name}',
            reply_markup=GameCreation)
        await sleep(5)
        if len(Opponents[message.from_user.id]) > 0:
            Choosing_opponent = InlineKeyboardMarkup(row_width=2)
            for i in range(len(Opponents[message.from_user.id])):
                Choosing_opponent.insert(InlineKeyboardButton(text=f"{Opponents[message.from_user.id][i][1]}",
                                                              callback_data=FutureOpponent.new(
                                                                  creator=message.from_user.id,
                                                                  opponent_id=Opponents[message.from_user.id][i][0],
                                                                  opponent_name=Opponents[
                                                                      message.from_user.id][i][1])))
            await bot.edit_message_text(chat_id=message.chat.id, message_id=game_creation.message_id,
                                        text='Выберите оппонента', reply_markup=Choosing_opponent)
            await sleep(60)
            if message.from_user.id in Opponents.keys():
                Opponents.pop(message.from_user.id)
                await bot.delete_message(chat_id=message.chat.id, message_id=game_creation.message_id)
        else:
            Opponents.pop(message.from_user.id)
            await bot.delete_message(chat_id=message.chat.id, message_id=game_creation.message_id)
    else:
        await message.answer(text='Игра уже существует, или вы уже находитесь в подборе противника.')


@dp.callback_query_handler(NWMPCreateGameData.filter(), state=None)
async def adding_opponents(callback: CallbackQuery, callback_data: dict):
    await bot.answer_callback_query(callback.id)
    if int(callback_data.get('creator')) != int(callback.from_user.id):
        for i in range(len(Opponents[int(callback_data.get('creator'))])):
            if Opponents[int(callback_data.get('creator'))][i][0] == int(callback.from_user.id):
                break
        else:
            new_opponent = (callback.from_user.id, callback.from_user.full_name)
            Opponents[int(callback_data.get('creator'))].append(new_opponent)


@dp.callback_query_handler(FutureOpponent.filter(), state=None)
async def creating_table(callback: CallbackQuery, callback_data: dict):
    await bot.answer_callback_query(callback.id)
    for i in range(len(Opponents[int(callback_data.get('creator'))])):
        if Opponents[int(callback_data.get('creator'))][i][0] == int(callback.from_user.id):
            break
    else:
        opponent_id = int(callback_data.get("opponent_id"))
        opponent_name = callback_data.get("opponent_name")
        creation_message = callback.message.message_id
        if (not db.game_exists(callback.from_user.id)) and (not db.game_exists(opponent_id)) and (
                callback.from_user.id in Opponents.keys()) and (opponent_id not in Opponents.keys()):
            Opponents.pop(callback.from_user.id)
            Players = {opponent_id: opponent_name, callback.from_user.id: callback.from_user.full_name}
            numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
            string_of_numbers = ''.join(random.choice(numbers) for i in range(10))
            players = [callback.from_user.id, opponent_id]
            order_of_game = random.sample(players, 2)
            next_turn, current_turn = map(int, order_of_game)
            Choosing_position = InlineKeyboardMarkup(row_width=5)
            for i in range(len(string_of_numbers)):
                Choosing_position.insert(
                    InlineKeyboardButton(text=f"{i + 1}", callback_data=NWMPGame.new(current_turn=current_turn,
                                                                                     str_pos=i)))
            db.add_game(callback.message.chat.id, callback.from_user.id, opponent_id, next_turn, string_of_numbers)
            await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=creation_message,
                                        text=f"Создана игра между игроками {callback.from_user.full_name} и {opponent_name}.")
            await bot.send_message(chat_id=callback.message.chat.id, text=f"Сначала ходит {Players[current_turn]}")
            msg_id = await bot.send_message(chat_id=callback.message.chat.id,
                                            text=f"Игроки:\n"
                                                 f"{callback.from_user.full_name} и {opponent_name}\n"
                                                 f"Текущая строка:\n"
                                                 f"{string_of_numbers}", reply_markup=Choosing_position)
            db.update_msg(callback.from_user.id, msg_id.message_id)
            await dp.storage.set_state(user=callback.from_user.id, chat=callback.message.chat.id,
                                       state=Modes.NumwarsMP.state)
            await dp.storage.set_state(user=opponent_id, chat=callback.message.chat.id, state=Modes.NumwarsMP.state)
        else:
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=creation_message)


@dp.message_handler(chat_type='group', commands='NWMPQuit', state=None)
@dp.message_handler(Text(equals='NWMPQuit', ignore_case=True), chat_type='group', state=None)
@dp.message_handler(chat_type='group', commands='NWMPQuit', state=Modes.NumwarsMP)
@dp.message_handler(Text(equals='NWMPQuit', ignore_case=True), chat_type='group', state=Modes.NumwarsMP)
async def NWMPQuitGame(message: Message):
    if db.game_exists(message.from_user.id):
        game = db.game_info(message.from_user.id)
        chat_id = game[1]
        p1 = game[2]
        p2 = game[3]
        msg = game[6]
        db.delete_game(message.from_user.id)
        await dp.storage.set_state(user=p1, chat=message.chat.id, state=None)
        await dp.storage.set_state(user=p2, chat=message.chat.id, state=None)
        await bot.delete_message(chat_id=chat_id, message_id=msg)
        await message.answer(text=f"Игра успешно удалена!")


@dp.message_handler(chat_type='group', commands='numwarsMP', state=None)
@dp.message_handler(Text(equals='numwarsMP', ignore_case=True), chat_type='group', state=None)
@dp.message_handler(chat_type='group', commands='numwarsMP', state=Modes.NumwarsMP)
@dp.message_handler(Text(equals='numwarsMP', ignore_case=True), chat_type='group', state=Modes.NumwarsMP)
async def numwarsMPGameStatus(message: Message, state: FSMContext):
    if db.game_exists(message.from_user.id):
        game = db.game_info(message.from_user.id)
        chat_id = game[1]
        p1 = game[2]
        p2 = game[3]
        next_turn = game[4]
        s = game[5]
        msg = game[6]
        if message.chat.id == chat_id:
            current_state = await state.get_state()
            if current_state == Modes.NumwarsMP.state:
                await dp.storage.set_state(user=p1, chat=message.chat.id, state=None)
                await dp.storage.set_state(user=p2, chat=message.chat.id, state=None)
                await message.reply(text="Игра выключена для двоих!")
            else:
                if message.from_user.id != next_turn:
                    await message.reply(text=f"Игра запущена для двоих! Сейчас ваш ход.")
                elif message.from_user.id == next_turn:
                    await message.reply(text=f"Игра запущена для двоих! Сейчас не ваш ход.")
                current_turn = 0
                if p1 != next_turn:
                    current_turn = p1
                elif p1 == next_turn:
                    current_turn = p2
                Choosing_position = InlineKeyboardMarkup(row_width=5)
                for i in range(len(s)):
                    Choosing_position.insert(
                        InlineKeyboardButton(text=f"{i + 1}", callback_data=NWMPGame.new(current_turn=current_turn,
                                                                                         str_pos=i)))
                msg_new = await bot.copy_message(chat_id=chat_id, from_chat_id=chat_id, message_id=msg,
                                                 reply_markup=Choosing_position)
                await bot.delete_message(chat_id=chat_id, message_id=msg)
                db.update_msg(current_turn, msg_new.message_id)
                await dp.storage.set_state(user=p1, chat=message.chat.id, state=Modes.NumwarsMP.state)
                await dp.storage.set_state(user=p2, chat=message.chat.id, state=Modes.NumwarsMP.state)


@dp.callback_query_handler(NWMPGame.filter(), state=Modes.NumwarsMP)
async def numwarsMPGame(callback: CallbackQuery, callback_data: dict):
    if callback.from_user.id == int(callback_data.get("current_turn")) and (
            callback.from_user.id != db.game_info(callback.from_user.id)[4]):
        user = callback.from_user.id
        game = db.game_info(user)
        db.update_next(user)
        n = int(callback_data.get("str_pos"))
        chat_id = game[1]
        p1 = game[2]
        p2 = game[3]
        next_turn = game[4]
        s = game[5]
        msg = game[6]
        s_pos = -1
        msg_text = [x for x in callback.message.text.split()]
        for i in range(len(msg_text)):
            if msg_text[i] == s:
                s_pos = i
                break
        if int(s[n]) > 0:
            s = s[:n] + str(int(s[n]) - 1) + s[n + 1:]
        else:
            s = s[:n]
        db.update_string(user, s)
        await bot.answer_callback_query(callback.id)
        if s == '':
            looser = await bot.send_message(chat_id=chat_id, text=f'Игрок {callback.from_user.full_name} проиграл.')
            if db.user_exists(next_turn):
                lvl_up(next_turn, 90)
                db.wins_update(next_turn)
            else:
                await bot.send_message(chat_id=chat_id, text=f'Победивший игрок, напиишите боту \"/start\" '
                                                             f'в личные сообщения, чтобы он мог обновлять вашу статистику.')
            if not db.user_exists(user):
                create_user(callback, user)
            db.loses_update(user)
            await bot.delete_message(chat_id=chat_id, message_id=msg)
            db.delete_game(user)
            await dp.storage.set_state(user=p1, chat=chat_id, state=None)
            await dp.storage.set_state(user=p2, chat=chat_id, state=None)
            cmt = ''
            for i in range(s_pos):
                if i == (s_pos - 3):
                    cmt = cmt + msg_text[i] + '\n'
                elif i == (s_pos - 1):
                    cmt = cmt + msg_text[i] + '\n'
                else:
                    cmt = cmt + msg_text[i] + ' '
            TextsForRecreating[p1] = cmt
            TextsForRecreating[p2] = cmt
            RecreateGame = InlineKeyboardMarkup(row_width=2)
            RecreateGame.insert(InlineKeyboardButton(text="Да",
                                                     callback_data=NWMPRecreateGame.new(answer="YES", p1=p1,
                                                                                        p2=p2, message=msg)))
            RecreateGame.insert(InlineKeyboardButton(text="Нет",
                                                     callback_data=NWMPRecreateGame.new(answer="NO", p1=p1,
                                                                                        p2=p2, message=msg)))
            recreation = await looser.reply(text=f'Хотите сыграть ещё?',
                                            reply_markup=RecreateGame)
            await sleep(10)
            try:
                await bot.delete_message(chat_id=recreation.chat.id, message_id=recreation.message_id)
                TextsForRecreating.pop(p1)
                TextsForRecreating.pop(p2)
            except:
                return None
        else:
            text = ''
            for i in range(s_pos):
                if i == (s_pos - 3):
                    text = text + msg_text[i] + '\n\n'
                elif i == (s_pos - 1):
                    text = text + msg_text[i] + '\n'
                else:
                    text = text + msg_text[i] + ' '
            text = text + s + '\n\n' + f"Игрок {callback.from_user.full_name} изменил цифру на позиции {n + 1}!"
            Choosing_position = InlineKeyboardMarkup(row_width=5)
            for i in range(len(s)):
                Choosing_position.insert(
                    InlineKeyboardButton(text=f"{i + 1}", callback_data=NWMPGame.new(current_turn=next_turn,
                                                                                     str_pos=i)))
            await bot.edit_message_text(chat_id=chat_id, message_id=msg, text=text, reply_markup=Choosing_position)
    else:
        await bot.answer_callback_query(callback.id)


@dp.callback_query_handler(NWMPGame.filter(), state=None)
@dp.callback_query_handler(NWMPGame.filter(), state=Modes.all_states_names)
async def numwarsMPGameAnswer(callback: CallbackQuery):
    await bot.answer_callback_query(callback.id)


@dp.callback_query_handler(NWMPRecreateGame.filter(), state=None)
async def recreating_game(callback: CallbackQuery, callback_data: dict):
    if (callback.from_user.id == int(callback_data.get("p1"))) or (
            callback.from_user.id == int(callback_data.get("p2"))):
        user = callback.from_user.id
        p1 = int(callback_data.get("p1"))
        p2 = int(callback_data.get("p2"))
        if (not db.game_exists(p1)) and (not db.game_exists(p2)) and (
                p1 not in Opponents.keys()) and (p2 not in Opponents.keys()):
            if callback_data.get("answer") == "YES":
                numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
                string_of_numbers = ''.join(random.choice(numbers) for i in range(10))
                if user == int(callback_data.get("p1")):
                    next_turn = p2
                    current_turn = p1
                else:
                    next_turn = p1
                    current_turn = p2
                Choosing_position = InlineKeyboardMarkup(row_width=5)
                for i in range(len(string_of_numbers)):
                    Choosing_position.insert(
                        InlineKeyboardButton(text=f"{i + 1}", callback_data=NWMPGame.new(current_turn=current_turn,
                                                                                         str_pos=i)))
                db.add_game(callback.message.chat.id, p1, p2, next_turn, string_of_numbers)
                await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
                await bot.send_message(chat_id=callback.message.chat.id,
                                       text=f"Новая игра создана! Начинает {callback.from_user.full_name}")
                msg_id = await bot.send_message(chat_id=callback.message.chat.id,
                                                text=f"{TextsForRecreating[user]}{string_of_numbers}",
                                                reply_markup=Choosing_position)
                db.update_msg(user, msg_id.message_id)
                TextsForRecreating.pop(p1)
                TextsForRecreating.pop(p2)
                await dp.storage.set_state(user=p1, chat=callback.message.chat.id, state=Modes.NumwarsMP.state)
                await dp.storage.set_state(user=p2, chat=callback.message.chat.id, state=Modes.NumwarsMP.state)
            elif callback_data.get("answer") == "NO":
                await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
                TextsForRecreating.pop(p1)
                TextsForRecreating.pop(p2)
    await bot.answer_callback_query(callback.id)


@dp.message_handler(commands='NWMP_top', chat_type='private')
@dp.message_handler(Text(equals='NWMP_top', ignore_case=True), chat_type='private')
async def NWMPTop(message: Message):
    user = message.from_user.id
    donate_status = db.get_info(user, 'donate_status')
    check_result = False
    if (donate_status != 1 and db.get_info(user, 'payment_status') != '0') or (db.get_info(user, 'lvl') >= 20):
        check_result = check_payment(user)
    if donate_status == 1 or db.get_info(user, 'lvl') >= 20 or check_result:
        Data = db.NWMP_rating()
        leaderboard = ''
        top_winners = sorted(Data, key=lambda x: x[1], reverse=True)
        for p in range(10):
            if p >= len(top_winners):
                break
            win_rate = 0
            if top_winners[p][1] != 0:
                win_rate = round(top_winners[p][1] / (top_winners[p][1] + top_winners[p][2]) * 100)
            leaderboard = leaderboard + f"{p + 1}) {top_winners[p][0]}: {top_winners[p][1]}(W) {top_winners[p][2]}(L) {win_rate}(%)\n"
        await message.answer(text=leaderboard)
    else:
        await message.answer(text="Функция заблокирована!")
        await payment(user)


# ADMIN COMMANDS


@dp.message_handler(commands='getinfo')
async def UserInfo(message: Message):
    if message.from_user.id == admin_id:
        await dp.storage.set_state(user=message.from_user.id, chat=message.chat.id, state=Modes.GetInfo.state)


@dp.message_handler(state=Modes.GetInfo, content_types=['text'])
async def UserInfo(message: Message, state: FSMContext):
    if message.from_user.id == admin_id:
        user = int(message.text)
        await message.answer(text=f"{db.get_info(user, 'url')}\n"
                                  f"id: {user}\n"
                                  f"Быки и коровы число: {db.get_info(user, 'BaC_number')}\n"
                                  f"Быки и коровы попытки: {db.get_info(user, 'BaC_attempts')}\n"
                                  f"Виселица слово: {db.get_info(user, 'gallows_word')}\n"
                                  f"Виселица предположние: {db.get_info(user, 'users_word')}\n"
                                  f"Виселица алфавит: {db.get_info(user, 'users_attempts')}\n"
                                  f"Ошибки: {db.get_info(user, 'users_faults')}\n"
                                  f"Длина строки: {db.get_info(user, 'str_length')}\n"
                                  f"Строка: {db.get_info(user, 'string_of_numbers')}\n"
                                  f"Опыт: {db.get_info(user, 'exp')}\n"
                                  f"Лвл: {db.get_info(user, 'lvl')}\n"
                                  f"Донатер: {db.get_info(user, 'donate_status')}\n"
                                  f"Платёж: {db.get_info(user, 'payment_status')}\n")
    await state.finish()


@dp.message_handler(commands='setdonation')
async def SetDonate(message: Message):
    if message.from_user.id == admin_id:
        await dp.storage.set_state(user=message.from_user.id, chat=message.chat.id, state=Modes.Donation.state)


@dp.message_handler(state=Modes.Donation, content_types=['text'])
async def UserInfo(message: Message, state: FSMContext):
    if message.from_user.id == admin_id:
        user, status = map(int, message.text.split())
        db.update_info(user, 'donate_status', status)
    await state.finish()


@dp.message_handler(commands='database', chat_type='private')
async def send_database_to_admin(message: Message):
    user = message.from_user.id
    
    if user != admin_id:
        await message.answer("⛔ У вас нет прав доступа к этой команде")
        return
    
    await send_database()


async def send_database():
    try:
        db_path = './data/database.db'
        
        await bot.send_document(chat_id=admin_id,
            document=InputFile(db_path),
            caption="📦 Актуальная копия базы данных"
        )
    except Exception as e:
        await bot.send_message(chat_id=admin_id, text=f"❌ Ошибка при отправке базы данных: {str(e)}")