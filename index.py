from jira import JIRA
import time
import telebot
import threading
from threading import Thread
class JiraSession:
    def __init__(self, login, password):
        self.jira = JIRA(options=self.jira_options, auth=(login, password))
        self.jira_login = login
        self.jira_password = password
        self.__unresolved_tasks_store = [] #здесь храним список открытых задач
        self.__prev_unresolved_tasks_store = [] #сюда задачи перемещаются перед обновлением основного стора
    TG_TOKEN = #INSERT_BOT_TOKEN
    bot = telebot.TeleBot(TG_TOKEN)

    base_url = #INSERT_JIRA_SERVER_URL
    jira_options = {'server': base_url} 
    jira = None
    is_subscribe = True
    jira_login = None
    jira_password = None
    jql = 'assignee = currentUser() AND resolution = Unresolved order by updated DESC' #Открытые задачи на мне


#Получаем список открытых задач пользователя
    def get_unresolved_tasks(self,store):
        self.__unresolved_tasks_store.clear()
        issues_list = self.jira.search_issues(self.jql) 
        string_of_unresolved_tasks = ''
        for issue in issues_list:
            string_of_unresolved_tasks += ('\n🔹' + self.base_url + '/browse/' + issue.key + ' :\n' + issue.fields.summary)"
            self.__unresolved_tasks_store.append(issue.key)
        if store == False:
            return string_of_unresolved_tasks 
        else:
            return self.__unresolved_tasks_store
        
#Проверяем наличие новых задач
    def fetch_new_issues(self, user_id):
        seconds = 30
        while True:
            if not self.is_subscribe:
                break
            self.__prev_unresolved_tasks_store = []
            for task in self.__unresolved_tasks_store:
                self.__prev_unresolved_tasks_store.append(task)
            self.__unresolved_tasks_store = self.get_unresolved_tasks(True)
            new_issues = (set(self.__unresolved_tasks_store) - set(self.__prev_unresolved_tasks_store))
            if  new_issues:
                for issue_key in new_issues:
                    issue = self.jira.issue(issue_key)
                    self.bot.send_message(user_id, ('⚠️На вас назначена новая задача⚠️\n🔹' + self.base_url + '/browse/' + issue.key + ' :\n' + issue.fields.summary))
            time.sleep(seconds)


        

