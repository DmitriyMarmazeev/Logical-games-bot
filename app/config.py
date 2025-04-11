import os

# Данные для бота

BOT_TOKEN = os.getenv("BOT_TOKEN")
PUBLIC_TOKEN = os.getenv("PUBLIC_TOKEN")
YOOMONEY_TOKEN = os.getenv("YOOMONEY_TOKEN")
YOOMONEY_WALLET = os.getenv("YOOMONEY_WALLET")
admin_id = int(os.getenv("admin_id"))
admin_url = f'<a href="tg://user?id={admin_id}">Админ</a>'


# Колонки таблицы

InfoTypes = {'db_id': [0, 0],
             'user_id': [1, 0],
             'url': [2, "UPDATE `UsersInfo` SET `url` = ? WHERE `user_id` = ?"],
             'BaC_number': [3, "UPDATE `UsersInfo` SET `BaC_number` = ? WHERE `user_id` = ?"],
             'BaC_attempts': [4, "UPDATE `UsersInfo` SET `BaC_attempts` = ? WHERE `user_id` = ?"],
             'gallows_word': [5, "UPDATE `UsersInfo` SET `gallows_word` = ? WHERE `user_id` = ?"],
             'users_word': [6, "UPDATE `UsersInfo` SET `users_word` = ? WHERE `user_id` = ?"],
             'users_attempts': [7, "UPDATE `UsersInfo` SET `users_attempts` = ? WHERE `user_id` = ?"],
             'users_faults': [8, "UPDATE `UsersInfo` SET `users_faults` = ? WHERE `user_id` = ?"],
             'str_length': [9, "UPDATE `UsersInfo` SET `str_length` = ? WHERE `user_id` = ?"],
             'string_of_numbers': [10, "UPDATE `UsersInfo` SET `string_of_numbers` = ? WHERE `user_id` = ?"],
             'exp': [11, "UPDATE `UsersInfo` SET `exp` = ? WHERE `user_id` = ?"],
             'lvl': [12, "UPDATE `UsersInfo` SET `lvl` = ? WHERE `user_id` = ?"],
             'donate_status': [13, "UPDATE `UsersInfo` SET `donate_status` = ? WHERE `user_id` = ?"],
             'payment_status': [14, "UPDATE `UsersInfo` SET `payment_status` = ? WHERE `user_id` = ?"]}


# КОМАНДЫ

'''start - Начало общения
help - Описание возможностей
bac - Игра "Быки и коровы"
gallows - Игра" Виселица"
numwars - Игра "Цифровые войны"
setstrlen - Установка длины строки в "Цифровых войнах"
back - Возвращение к выбору режима
lvl - Показывает ваш уровень
top - Выводит топ 10 пользователей по уровню
nwmp_top - Выводит топ 10 игроков по победам в NumwarsMP
editname - Преображает ваше имя в топе
nwmpcreate - Создаёт игру "Цифровые войны MP"
nwmpquit - Удаляет игру "Цифровые войны MP"
numwarsmp - Включает или выключает игру "Цифровые войны MP"'''


# ВИСЕЛИЦА

gallows_stages = [
    """
--------
    """,
    """
|
|
|
|
|
--------
    """,
    """
------
|
|
|
|
|
--------
    """,
    """
------
|    |
|
|
|
|
--------
    """,
    """
------
|    |
|    O
|
|
|
--------
    """,
    """
------
|    |
|    O
|    |
|
|
--------
    """,
    """
------
|    |
|    O
|   /|
|
|
--------
    """,
    """
------
|    |
|    O
|   /|\\
|
|
--------
    """,
    """
------
|    |
|    O
|   /|\\
|   / 
|
--------
    """,
    """
------
|    |
|    O
|   /|\\
|    / \\
|
--------
    """
]


# СЛОВАРЬ


slovar = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZzАаБбВвГгДдЕеЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя1234567890 " + chr(203) + chr(203).lower() + chr(1025) + chr(1025).lower()
