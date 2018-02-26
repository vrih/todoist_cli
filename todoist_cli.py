"""CLI for todoist"""
import argparse
from datetime import datetime, timezone
import logging
import os
from typing import List, Dict, Union

import requests
from todoist.api import TodoistAPI

import completions
import data_accessor as da
import input_parser as ip
import renderer as rd

def sync():
    """Sync with todoist API"""
    api = TodoistAPI(os.getenv("TODOIST_TOKEN"))
    api.sync()
    return api

def arg_parser():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('command')
    parser.add_argument('--task', '-t', dest='task', default=0, nargs="+", required=False)
    parser.add_argument('--project', '-p', dest='project', default=None, required=False)
    parser.add_argument('--date', '-d', dest='date', default=None, required=False)
    parser.add_argument('--content', '-c', dest='content', default=None, required=False)
    parser.add_argument('--labels', '-l', dest='labels', default=None, nargs="+", required=False)
    parser.add_argument('--priority', '-P', dest='priority', default=None, required=False)
    return parser.parse_args()

def is_skippable(item) -> bool:
    """Should item be skipped"""
    try:
        if item['is_deleted'] == 1:
            return True
    except KeyError:
        pass

    # don't show checked tasks
    try:
        if item['checked'] == 1:
            return True
    except KeyError:
        pass
    return False

def date_skippable(delta: int, date: str) -> bool:
    "Return string representation of output date deltae"
    if date == "today" and delta > 0:
        return True
    if date == "tomorrow" and delta != 1:
        return True
    if delta > 7:
        return True
    return False


def date_delta_to_str(delta: int, item_date) -> str:
    """Convert date delta to human format"""
    return {0: "Today", 1: "Tomorrow"}.get(delta, datetime.strftime(item_date, "%A"))

def print_all_tasks(project=None, date: str = None):
    """Pretty print all tasks"""
    # bootstrap dictionary from projects table
    project_table = da.project_ids()
    output_table: Dict[int, List[Union[None, Dict]]] = {i['id']: [] for i in API.state['projects']}

    # fill with tasks
    for i in API.state['items']:
        # don't show deleted tasks
        if is_skippable(i):
            continue

        output_date = "Unknown"
        item_date = None

        try:
            if i['due_date_utc']:
                item_date = datetime.strptime(i['due_date_utc'],
                                              "%a %d %b %Y %H:%M:%S %z")
                now = datetime.now(timezone.utc)
                # ensure we are looking at the end of tomorrow
                date_delta = (item_date.replace(hour=23, minute=59, second=59) - now).days

                if date_skippable(date_delta, date):
                    continue

                output_date = date_delta_to_str(date_delta, item_date)

                if item_date.hour != 23:
                    output_date += f" {item_date.hour}:{item_date.minute:02d}"

            else:
                item_date = datetime.now(timezone.utc)
        except KeyError as error:
          #  logging.error("Key error: %s:  %s", error, i)
            continue
            #item_date = datetime.now(timezone.utc)
        label_d = da.label_ids()

        try:
            item = {
                'id': i['id'],
                'due_date': output_date,
                'content': i['content'],
                'sys_date': item_date,
                'priority': 5 - i['priority'],
                'labels': ','.join([label_d[j] for j in i['labels']])}

            output_table[i['project_id']].append(item)
        except TypeError as error:
            logging.error("TypeError: %s: %s", error, i)
            continue

    rd.render_output_table(output_table.items(), project, project_table)

def complete_task(tasks: List[int]):
    # Todo: accept multiple tasks
    task_d = da.task_ids()

    for task in tasks:
        API.items.close(task)

    try:
        API.commit()
    except requests.exceptions.ConnectionError:
        print("Connection error. Try again")

    for task in tasks:
        print("Task \"{}\" completed".format(task_d[task]))


def delete_task(tasks):
    """Delete task from todoist"""
    # Todo: accept multiple tasks
    task_d = da.task_ids()

    for task in tasks:
        item = API.items.get_by_id(int(task))
        item.delete()
    try:
        API.commit()
    except requests.exceptions.ConnectionError:
        logging.error("Connection error. Try again")

    for task in tasks:
        print("Task \"{}\" deleted".format(task_d[int(task)]))

def add_task(text, project: str, date: str, labels, priority: int):
    """Add task to todoist"""
    projects = da.project_names()
    label_d = da.label_names()
    # convert from computer to human priority
    if priority:
        priority = 5 - int(priority)

    if project == 0:
        project = None

    if labels:
        labels = [label_d[i] for i in labels]

    API.items.add(text, project_id=projects[project],
                  date_string=date, priority=priority, labels=labels)

    try:
        API.commit()
    except requests.exceptions.ConnectionError:
        logging.error("Connection error. Try again")
    print("{} added".format(text))

def update_task(tasks, date, content, labels, priority):
    api = API
    label_d = da.label_names()

    for task in tasks:
        if date:
            api.items.update(task, date_string=date)
        if content:
            api.items.update(task, content=content)
        if labels:
            api.items.update(task, labels=[label_d[i] for i in labels])
        if priority:
            pri = 5 - int(priority)
            api.items.update(task, priority=pri)

    try:
        api.commit()
    except requests.exceptions.ConnectionError:
        logging.error("Connection error. Try again")
    print("{} updated".format(tasks))


def interactive_list(args) -> None:
    """List interactively"""
    try:
        date = args[args.index("-d") + 1]
    except ValueError:
        date = None

    try:
        project = args[args.index("-p") + 1]
    except ValueError:
        project = None
    print_all_tasks(project=project, date=date)

def interactive_update() -> None:
    """Update a task interactively"""
    print_all_tasks()
    task_to_update = ip.get_task()
    content = input("content: ")
    if content == "":
        content = None
    due = ip.get_due()
    priority = ip.get_priority()
    labels = ip.get_labels()
    update_task([task_to_update], due, content, labels, priority)

def interactive_add() -> None:
    """Add a task interactively"""
    content = input("content: ")
    project = ip.get_project()
    due = ip.get_due()
    priority = ip.get_priority()
    labels = ip.get_labels()
    add_task(content, project, due, labels, priority)

def interactive() -> None:
    """Start an interactive session"""
    import readline
    import shlex

    readline.parse_and_bind("tab: complete")
    while True:
        readline.set_completer(completions.complete)
        try:
            command = input("(todoist) ")
        except KeyboardInterrupt:
            return

        args = shlex.split(command)

        try:
            if not args:
                continue
            elif args[0] == "list":
                interactive_list(args)
            elif args[0] == "complete":
                print_all_tasks()
                task_to_complete = ip.get_task()
                complete_task([task_to_complete])
            elif args[0] == "delete":
                print_all_tasks()
                task_to_delete = ip.get_task()
                delete_task([task_to_delete])
            elif args[0] == "update":
                interactive_update()
            elif args[0] == "add":
                interactive_add()
            elif args[0] == "projects":
                for project in da.project_names():
                    print(project)
            elif args[0] == "quit":
                return
        except KeyboardInterrupt:
            print("")
            continue

if __name__ == "__main__":
    ARGS = arg_parser()
    API = sync()

    da.API = API

    OUTPUT_TABLE: Dict = {}

    TASKS: List[int] = []

    if ARGS.task:
        TASKS = [int(task, 16) for task in ARGS.task]

    if ARGS.command == "interactive":
        interactive()
    elif ARGS.command == "list":
        print_all_tasks(project=ARGS.project, date=ARGS.date)
    elif ARGS.command == "complete":
        if TASKS:
            complete_task(TASKS)
    elif ARGS.command == "delete":
        if TASKS:
            delete_task(TASKS)
    elif ARGS.command == "add":
        add_task(ARGS.content, ARGS.project, ARGS.date, ARGS.labels, ARGS.priority)
    elif ARGS.command == "update":
        update_task(TASKS, ARGS.date, ARGS.content, ARGS.labels, ARGS.priority)
