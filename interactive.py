"""Interactive todoist"""
from typing import List

import completions
import input_parser as ip
import renderer as rd
import data_accessor as da
import todoist_calls as td

def view(args, date=None) -> None:
    """List interactively"""
    try:
        if not date:
            date = args[args.index("-d") + 1]
    except ValueError:
        date = None

    try:
        project = args[args.index("-p") + 1]
    except ValueError:
        project = None
    rd.print_all_tasks(project=project, date=date)

def today(args) -> None:
    """List tasks for today"""
    view(args, date="today")

def tomorrow(args) -> None:
    """List tasks for tomorrow"""
    view(args, date="tomorrow")

def update(_) -> None:
    """Update a task interactively"""
    rd.print_all_tasks()
    task_to_update = ip.get_task()
    content = input("content: ")
    if content == "":
        content = None
    due = ip.get_due()
    priority = ip.get_priority()
    labels = ip.get_labels()
    td.update_task([task_to_update], due, content, labels, priority)

def add(_) -> None:
    """Add a task interactively"""
    content = input("content: ")
    project = ip.get_project()
    due = ip.get_due()
    priority = ip.get_priority()
    labels = ip.get_labels()
    td.add_task(content, project, due, labels, priority)

def end_task(args, func):
    """Helper for ending tasks"""
    if len(args) > 1:
        tasks = [int(t, 16) for t in args[1:]]
    else:
        rd.print_all_tasks()
        tasks = [ip.get_task()]
    func(tasks)

def complete(args: List[str]) -> None:
    """Complete a task interactively"""
    end_task(args, td.complete_task)

def delete(args: List[str]) -> None:
    """Delete a task interactively"""
    end_task(args, td.delete_task)

def comments(args: List[str]) -> None:
    """Render cmments"""
    ### TODO: Move to render function and make pretty
    if len(args) > 1:
        task = int(args[1], 16)
    else:
        rd.print_all_tasks()
        task = ip.get_task()

    for comment in da.notes(task):
        print(f"{comment['posted']}:\n{comment['content']}\n")


def projects(_) -> None:
    """Print all projects"""
    for project in da.project_names():
        print(project)

def sync(_) -> None:
    """Resync"""
    td.sync()

FUNCTIONS = {
    "list": view,
    "today": today,
    "tomorrow": tomorrow,
    "complete":complete,
    "delete": delete,
    "update": update,
    "add": add,
    "projects": projects,
    "comments": comments,
    "sync": sync
}

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

            FUNCTIONS[args[0]](args)
        except KeyError:
            continue
        except KeyboardInterrupt:
            print("")
            continue
