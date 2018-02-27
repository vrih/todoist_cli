"""Functions talking directly to todoist"""
import logging
import os
from typing import List, Optional

import requests
from todoist.api import TodoistAPI

import data_accessor as da

API = TodoistAPI(os.getenv("TODOIST_TOKEN"))

def sync():
    """Sync with todoist API"""
    API.sync()

def commit() -> bool:
    """Commit to API"""
    try:
        API.commit()
    except requests.exceptions.ConnectionError:
        logging.error("Connection error. Try again")
        return False
    return True

def complete_task(tasks: List[int]):
    """Mark tasks as complete"""
    task_d = da.task_ids()

    for task in tasks:
        API.items.close(task)

    if commit():
        for task in tasks:
            print("Task \"{}\" completed".format(task_d[task]))


def delete_task(tasks):
    """Delete task from todoist"""
    task_d = da.task_ids()

    for task in tasks:
        item = API.items.get_by_id(int(task))
        item.delete()

    if commit():
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

    if commit():
        print("{} added".format(text))

def update_task(tasks: List[int], date: Optional[str], content: Optional[str],
                labels: Optional[List[str]], priority: Optional[int]):
    """Update task"""
    label_d = da.label_names()

    for task in tasks:
        if date:
            API.items.update(task, date_string=date)
        if content:
            API.items.update(task, content=content)
        if labels:
            API.items.update(task, labels=[label_d[i] for i in labels])
        if priority:
            pri = 5 - int(priority)
            API.items.update(task, priority=pri)

    if commit():
        print("{} updated".format(tasks))
