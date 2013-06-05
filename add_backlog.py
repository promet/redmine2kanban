#!/usr/bin/env python
import json
import requests
import sys
import datetime

# Kanban board number
# If your kanbanery board URL is
# https://promet.kanbanery.com/projects/6880/board/
# then
# 6880 is your board number
active_board_num = 6880

# Archive board number
# This monitors your archived board and prevents dupes
archive_board_num = 5988

# Status id: 
# 1 -> new, 
# 2 -> assigned

# prod kanbanery token of user some_user
KanbanToken = "KANBAN_API_KEY" 

# prod redmine token of user some_user 
RedmineToken = "SOME_USERS_API_KEY" 

# Url of promet redmine
RedmineUrl = "projects.prometsupport.com"

# id of your kanban [name].kanbanery.com
KanbanName = "name" 

# Group individual redmine ids
# sysadmin_user, Gerold, Greg, Marius
ids = [146,8,156,6] 

# list of issues need to be skipped
# If you have issues that you want excluded, put them in this array
skip_issues = [16334,25734,26810]

def main():
    """ main """
    redmine_add_kanban()
    marketing()
    # TODO: move task in kanban to Done column, etc

def add_to_kanban(issue_id, subject, task_type="bug", project=active_board_num, desc=""):
    """ add a ticket to kanban """
    subject = subject.replace(' ', '%20')
    kanban_task_title = u"%23{0}:%20{1}".format(str(issue_id), subject)
    print "\n---", datetime.datetime.now(), "---"
    print kanban_task_title.replace("%20", " ").replace("%23", "#")
    #print "Task type:", task_type, " in kanban board: ", project
    print 

    r = requests.post(u"https://promet.kanbanery.com/api/v1/projects/{0}/tasks.json?task[task_type_name]={1}&task[title]={2}&task[description]={3}".format(project, task_type, kanban_task_title, desc), headers={"X-Kanbanery-ApiToken": KanbanToken})
    #print r.status_code
    if r.status_code > 399:
        print r.text
        sys.exit(1)

def get_kanban_task_titles(project=archive_board_num):
    """ Look for issues already on Kanban (by looking at issue number in title) """
    titles = "" 
    r = requests.get(u"https://promet.kanbanery.com/api/v1/projects/{0}/tasks.json".format(project), headers={"X-Kanbanery-ApiToken": KanbanToken})
    #print "Fetched tasks title in kanban: ", r.status_code
    if r.status_code > 399:
        print r.text
        sys.exit(1)

    raw = json.loads(r.text)
    for item in raw:
        titles += item['title']

    r = requests.get(u"https://promet.kanbanery.com/api/v1/projects/{0}/icebox/tasks.json".format(project), headers={"X-Kanbanery-ApiToken": KanbanToken})
    if r.status_code > 399:
        print r.text
        sys.exit(1)

    raw = json.loads(r.text)
    for item in raw:
        titles += item['title']

    return titles

def redmine_add_kanban():
    """ fetch tickets assigned to certain users and create those in Kanban """ 
    titles = get_kanban_task_titles(active_board_num)

    for id in ids:
        r = requests.get(u"http://{0}/issues.json?assigned_to_id={1}&limit=5000".format(RedmineUrl, id), headers={"Content-Type":"application/json", "X-Redmine-API-Key":RedmineToken})
        #print "Fetched issues assigned to {0} in redmine: ".format(id), r.status_code

        if r.status_code > 399:
            print r.text
            sys.exit(1)
        raw = json.loads(r.text)

        for item in raw['issues']:
            if int(item['id']) not in skip_issues and str(item['id']) not in titles:
                project = "6880"
                #print "Kanban:", project, " doesn't have ticket ", item['id']
                #print
                kanban_task_type = item['project']['id'] == 441 and "devops" or "servers"
                desc = u"https://projects.prometsupport.com/issues/{0}\n".format(item['id'])
                desc += item['description'] 
                add_to_kanban(int(item['id']), item['subject'], kanban_task_type, project, desc)

if __name__ == '__main__':
    main()
