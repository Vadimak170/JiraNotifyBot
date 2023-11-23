import telebot
from telebot import types
import index 
import mysql.connector
import threading
from threading import Thread
def main():
    DEBUG = 0
    TG_TOKEN = #INSERT_BOT_TOKEN
    bot = telebot.TeleBot(TG_TOKEN)
    SessionsStore = {}
    #Подключаем на рассылку  авторизованных юзеров при перезапуске приложения
    def sessions_restore():
        auth_user = get_session_data()
        for user in auth_user:
                id = user[0]
                login = user[1]
                password = user[2]
                try:
                    SessionsStore[id] = index.JiraSession(login,password)
                    print('Restored session for:' + str(SessionsStore[id].jira_login))
                    SessionsStore[id].get_unresolved_tasks(True)
                    thread = Thread(target=SessionsStore[id].fetch_new_issues,args=([id]))
                    thread.start()
                except:
                    if DEBUG:  
                        raise
                    bot.send_message(*YOUR TELEGRAM ID HERE*, '😢Не могу восстановить сессию!Логин:' + login)

    #Получаем данные об авторизованных юзерах из БД
    def get_session_data():
        connection = mysql.connector.connect(user=*MySQL_login*,password=*MySQL_password*, database = *MySQL_db*, host=*MySQL_host*, port = *MySQL_port*)
        cursor=connection.cursor()
        #TABLE session_data id = bigint, login = VARCHAR(100), password = VARCHAR(100)
        sql ='select id, login, password from session_data'

        cursor.execute(sql)
        session_data = cursor.fetchall()
        connection.close()
        return session_data
    
    def new_user(id,login,password):
        connection = mysql.connector.connect(user=*MySQL_login*,password=*MySQL_password*, database = *MySQL_db*, host=*MySQL_host*, port = *MySQL_port*)
        cursor=connection.cursor()

        sql =f'INSERT INTO session_data VALUES ({id}, "{login}", "{password}")'

        cursor.execute(sql)
        connection.commit()
        connection.close()

    def del_user(id):
        connection = mysql.connector.connect(user=*MySQL_login*,password=*MySQL_password*, database = *MySQL_db*, host=*MySQL_host*, port = *MySQL_port*)
        cursor=connection.cursor()

        sql =f'DELETE FROM session_data WHERE ID = {id}'

        cursor.execute(sql)
        connection.commit()
        connection.close()
    def logout(id):
        SessionsStore[id].is_subscribe = False
        del_user(id)
        del SessionsStore[id]
    sessions_restore()
    @bot.message_handler(commands=['start'])
    def start(message):
        if  message.from_user.id not in SessionsStore:
            try:
                bot.send_message(message.from_user.id, '👻Приветсвую!👻\n❗️Для того, что бы получать уведомления необходимо авторизоваться в Джире с помощью команды:\n  /auth *ТУТ ВАШ ЛОГИН*  *ТУТ ВАШ ПАРОЛЬ*\nПример:  /auth ivan.pupkin  pupkin_pas3219\n❗️Если больше не хотите получать уведомления, или сменили пароль в джире просто напишите "Выход"\n❗️Проверка новых задач происходит раз в 30 секунд!') 
            except:
                if DEBUG:  
                    raise
                print('Ошибка при старте')       

    @bot.message_handler(commands=['auth'])
    def auth(message):
        if  message.from_user.id not in SessionsStore:
            if len(message.text.split()) == 3:
                login = message.text.split()[1]
                passsword = message.text.split()[2]
                try:
                    SessionsStore[message.from_user.id] = index.JiraSession(login,passsword)
                    new_user(message.from_user.id, login, passsword)
                except:
                    bot.send_message(message.from_user.id, '😢Неверый логин или пароль!')

                try:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.row('📥Мои открытые задачи📥', 'Выход')
                    bot.send_message(message.from_user.id, '📝Ваши задачи на текущий момент: ' + SessionsStore[message.from_user.id].get_unresolved_tasks(False), reply_markup=markup)
                    thread = Thread(target=SessionsStore[message.from_user.id].fetch_new_issues,args=([message.from_user.id]))
                    thread.start()
                except:
                    if DEBUG:  
                        raise
                    print('Ошибка при отправке списка задач')
                    pass
            else:
                bot.send_message(message.from_user.id, '😢Неверый формат ввода!')
        else:
            bot.send_message(message.from_user.id, 'Вы уже авторизованы😅 Если хотите перезайти, напишите "Выход"')


    @bot.message_handler(content_types=['text'])
    def send_text(message):
        try:
            if  message.from_user.id  in SessionsStore:
                if message.text == '📥Мои открытые задачи📥':
                    bot.send_message(message.from_user.id, '📝Ваши задачи на текущий момент: ' + SessionsStore[message.from_user.id].get_unresolved_tasks(False))

                if message.text.lower() == 'выход':
                    try:
                        logout(message.from_user.id)
                        bot.send_message(message.from_user.id, '✅Выход. Вы больше не будете получать обновлений. \nЕсли захотите вернуться необходимо авторизоваться заново!')
                    except:
                        print('Ошибка выхода')
            else:
                bot.send_message(message.from_user.id, '❌Вы не авторизованы!')
        except:
            if DEBUG:  
                raise
            pass
    bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть

if __name__ == "__main__":
    while True:
        try:
            main()
        except:
            TG_TOKEN = #INSERT_BOT_TOKEN
            bot = telebot.TeleBot(TG_TOKEN)
            bot.send_message(*YOUR TG ID*, 'Непредвиденное завершение работы😓')
        