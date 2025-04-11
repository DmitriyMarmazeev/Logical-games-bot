import sqlite3

from config import InfoTypes


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    '''ТАБЛИЦА UsersInfo'''

    '''РАБОТА С ПОЛЬЗОВАТЕЛЕМ'''

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `UsersInfo` WHERE `user_id` = ?", (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id, url):
        with self.connection:
            self.cursor.execute("INSERT INTO `UsersInfo` (`user_id`) VALUES (?)", (user_id,))
            return self.cursor.execute("UPDATE `UsersInfo` SET `url` = ? WHERE `user_id` = ?", (url, user_id,))

    def get_info(self, user_id, info_type):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `UsersInfo` WHERE `user_id` = ?", (user_id,)).fetchone()
            return result[InfoTypes[info_type][0]]

    def update_info(self, user_id, info_type, value):
        with self.connection:
            return self.cursor.execute(InfoTypes[info_type][1], (value, user_id,))

    '''ПОБЕДЫ/ПОРАЖЕНИЯ В ЦИФРОВЫХ ВОЙНАХ MP'''

    def wins_update(self, user_id):
        with self.connection:
            wins = self.cursor.execute("SELECT `NWMP_Wins` FROM `UsersInfo` WHERE `user_id` = ?",
                                       (user_id,)).fetchone()
            self.cursor.execute("UPDATE `UsersInfo` SET `NWMP_Wins` = ? WHERE `user_id` = ?", (wins[0] + 1, user_id,))

    def loses_update(self, user_id):
        with self.connection:
            loses = self.cursor.execute("SELECT `NWMP_Loses` FROM `UsersInfo` WHERE `user_id` = ?",
                                        (user_id,)).fetchone()
            self.cursor.execute("UPDATE `UsersInfo` SET `NWMP_Loses` = ? WHERE `user_id` = ?", (loses[0] + 1, user_id,))

    '''РЕЙТИНГ'''

    '''ПО УРОВНЮ'''

    def rating(self):
        with self.connection:
            result = self.cursor.execute("SELECT `user_id`, `url`, `exp`, `lvl` FROM `UsersInfo`").fetchall()
            return result

    '''ПО ПОБЕДАМ В ЦИФРОВЫХ ВОЙНАХ MP'''

    def NWMP_rating(self):
        with self.connection:
            result = self.cursor.execute("SELECT `url`, `NWMP_Wins`, `NWMP_Loses` FROM `UsersInfo`").fetchall()
            return result

    '''ТАБЛИЦА NumwarsMP'''

    '''ОБРАБОТКА ЦИФРОВЫХ ВОЙН MP'''

    def game_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `NumwarsMP` WHERE ((`p1` = ?) OR (`p2` = ?))",
                                         (user_id, user_id,)).fetchall()
            return bool(len(result))

    def add_game(self, chat_id, creator, opponent, next_turn, string_of_numbers):
        with self.connection:
            self.cursor.execute(
                "INSERT INTO `NumwarsMP` (`chat_id`, `p1`, `p2`, `next_turn`, `string`) VALUES (?, ?, ?, ?, ?)",
                (chat_id, creator, opponent, next_turn, string_of_numbers,))

    def delete_game(self, player):
        with self.connection:
            self.cursor.execute("DELETE FROM `NumwarsMP` WHERE ((`p1` = ?) OR (`p2` = ?))", (player, player,))

    def game_info(self, player):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `NumwarsMP` WHERE ((`p1` = ?) OR (`p2` = ?))",
                                       (player, player,)).fetchone()

    '''ОБНОВЛЕНИЕ ДАННЫХ ЦИФРОВЫХ ВОЙН MP'''

    def update_string(self, player, string_of_numbers):
        with self.connection:
            self.cursor.execute("UPDATE `NumwarsMP` SET `string` = ? WHERE ((`p1` = ?) OR (`p2` = ?))",
                                (string_of_numbers, player, player,))

    def update_next(self, player):
        with self.connection:
            self.cursor.execute("UPDATE `NumwarsMP` SET `next_turn` = ? WHERE ((`p1` = ?) OR (`p2` = ?))",
                                (player, player, player,))

    def update_msg(self, player, msg_id):
        with self.connection:
            self.cursor.execute("UPDATE `NumwarsMP` SET `msg_id` = ? WHERE ((`p1` = ?) OR (`p2` = ?))",
                                (msg_id, player, player,))

    '''EVENTS'''

    def participant_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `EventParticipants` WHERE `user_id` = ?", (user_id,)).fetchall()
            return bool(len(result))

    def add_participant(self, user_id, full_name):
        with self.connection:
            self.cursor.execute("INSERT INTO `EventParticipants` (`user_id`, `Full_Name`) VALUES (?, ?)",
                                (user_id, full_name,))

    def get_all_participants(self):
        with self.connection:
            result = self.cursor.execute("SELECT `user_id` FROM `EventParticipants`").fetchall()
            return result

    def get_participant_name(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `Full_Name` FROM `EventParticipants` WHERE `user_id` = ?",
                                         (user_id,)).fetchone()
            return result[0]

    def add_event_game(self, creator, opponent, next_turn, string_of_numbers):
        with self.connection:
            self.cursor.execute(
                "INSERT INTO `EventTable` (`p1`, `p2`, `next_turn`, `string`) VALUES (?, ?, ?, ?)",
                (creator, opponent, next_turn, string_of_numbers,))

    def participant_won(self, user_id):
        with self.connection:
            self.cursor.execute("UPDATE `EventParticipants` SET `next_round` = 1 WHERE `user_id` = ?", (user_id,))

    def event_update_msg(self, player, msg_id):
        with self.connection:
            self.cursor.execute("UPDATE `EventTable` SET `msg_id` = ? WHERE ((`p1` = ?) OR (`p2` = ?))",
                                (msg_id, player, player,))

    def event_info(self, player):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `EventTable` WHERE ((`p1` = ?) OR (`p2` = ?))",
                                       (player, player,)).fetchone()

    def event_update_string(self, player, string_of_numbers):
        with self.connection:
            self.cursor.execute("UPDATE `EventTable` SET `string` = ? WHERE ((`p1` = ?) OR (`p2` = ?))",
                                (string_of_numbers, player, player,))

    def event_update_next(self, player):
        with self.connection:
            self.cursor.execute("UPDATE `EventTable` SET `next_turn` = ? WHERE ((`p1` = ?) OR (`p2` = ?))",
                                (player, player, player,))

    def get_all_games(self):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `EventTable` WHERE `game_ended` = 1").fetchall()
            return len(result)

    def game_won(self, player):
        with self.connection:
            self.cursor.execute("UPDATE `EventTable` SET `game_ended` = 1 WHERE ((`p1` = ?) OR (`p2` = ?))",
                                (player, player,))

    def delete_losers(self):
        with self.connection:
            self.cursor.execute("DELETE FROM `EventParticipants` WHERE `next_round` = 0")

    def clear_event_table(self):
        with self.connection:
            self.cursor.execute("DELETE FROM `EventTable`")

    def clear_event(self):
        with self.connection:
            self.cursor.execute("DELETE FROM `EventTable`")
            self.cursor.execute("DELETE FROM `EventParticipants`")

    def reset_winners(self):
        with self.connection:
            self.cursor.execute("UPDATE `EventParticipants` SET `next_round` = 0")

    def reload_status_get(self, player):
        with self.connection:
            result = self.cursor.execute("SELECT `reloading` FROM `EventTable` WHERE ((`p1` = ?) OR (`p2` = ?))",
                                         (player, player,)).fetchone()
        return result[0]

    def reload_event(self, status, player):
        with self.connection:
            self.cursor.execute("UPDATE `EventTable` SET `reloading` = ? WHERE ((`p1` = ?) OR (`p2` = ?))",
                                (status, player, player,))

    def avoid_flood(self):
        with self.connection:
            self.cursor.execute("UPDATE `EventTable` SET `reloading` = 0")
