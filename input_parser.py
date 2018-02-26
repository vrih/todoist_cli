"""Input gathering functions"""
import readline
from typing import List, Union

import completions

def get_project() -> str:
    """Take user input and return project"""
    readline.set_completer(completions.project_complete)
    project = input("project: ")
    if project == "":
        project = None
    return project

def get_due() -> Union[None, str]:
    """Take user input and return date"""
    readline.set_completer(completions.date_complete)
    due = input("due: ")
    if due == "":
        return None
    return due

def get_labels() -> Union[None, List[str]]:
    """Take user input and return list of labels"""
    readline.set_completer(completions.label_complete)
    labels = input("labels: ")
    if labels == "":
        return None
    return labels.split(",")

def get_priority() -> Union[None, int]:
    """Take user input and return priority"""
    while True:
        priority = input("priority: ")
        if priority == "":
            return None
        if priority not in [1, 2, 3, 4, 5]:
            print("Priority must be between 1 and 5")
            continue
        return int(priority)

def get_task() -> int:
    """Take user input and return task"""
    readline.set_completer(completions.task_complete)
    return int(input("task: "), 16)
