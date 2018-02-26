"""Completion functions for readline"""
import data_accessor as da

def complete(text, state):
    """Tab complete"""
    projects = list(da.project_names().keys())
    date = ["today", "tomorrow"]

    completions = projects
    completions.extend(date)

    for project in completions:
        if project.startswith(text):
            if not state:
                return project
            else:
                state -= 1
    return None

def project_complete(text, state):
    """Tab complete for projects"""
    for project in da.project_names():
        if project.startswith(text):
            if not state:
                return project
            else:
                state -= 1
    return None

def label_complete(text, state):
    """Tab complete for projects"""
    for label in da.label_names():
        if label.startswith(text):
            if not state:
                return label
            else:
                state -= 1
    return None

def date_complete(text, state):
    """Tab complete for dates"""
    dates = ["today", "tomorrow", "next week", "monday", "tuesday", "wednesday",
             "thursday", "friday", "saturday", "sunday"]

    for date in dates:
        if date.startswith(text):
            if not state:
                return date
            else:
                state -= 1
    return None

def task_complete(text, state):
    """Tab compelte for task IDs"""
    tasks = da.incomplete_task_ids()

    for task_id in tasks:
        if task_id.startswith(text):
            if not state:
                return task_id
            else:
                state -= 1
    return None
