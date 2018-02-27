"""Functions for rendering"""
from datetime import datetime, timezone
import logging
import operator
from typing import ItemsView, Dict, List, Union

from tabulate import tabulate

import data_accessor as da
import todoist_calls as td

def insert_color(color, text):
    """Wrap text in color"""
    return color + str(text) + "\033[0m"

def print_colored(text, priority):
    """Map priority to colors"""
    if priority == 1:
        return insert_color("\033[31m", text)
    if priority == 2:
        return insert_color("\033[33m", text)
    if priority == 3:
        return insert_color("\033[35m", text)
    return text

def construct_content(item, note_ids) -> str:
    if item['id'] in note_ids:
        return item['content'] + " 💬"
    return item['content']


def render_output_table(items: ItemsView, project, project_table) -> None:
    """Construct and print pretty table"""
    note_ids = da.note_ids()

    tasks_rendered = False
    for i, data in items:
        # for specified prject skip if not correct
        if project and project != project_table[i]:
            continue
        try:
            values = sorted(data, key=operator.itemgetter('sys_date', 'priority'))
            output_values = []
            for j in values:
                output_a = ['{:x}'.format(j['id']), j['due_date'], construct_content(j, note_ids),
                                  j.get('labels', "")]
                output_values.append([print_colored(x, j['priority']) for x in output_a])
            if output_values:
                tasks_rendered = True
                print(project_table[i])
                print(tabulate(output_values, headers=["ID", "Due", "Content", "Labels"],
                               tablefmt="fancy_grid"))
                print("")
        except KeyError as error:
            logging.error("Missing key: %s: %s", error, output_values)
        except TypeError as error:
            logging.error("Type error: %s: %s", error, i)
        except ValueError as error:
            logging.error("Value error: %s: %s", error, i)
    if not tasks_rendered:
        print("All tasks completed! 🙌")

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
    output_table: Dict[int, List[Union[None, Dict]]] = {i['id']: [] for i in td.API.state['projects']}

    # fill with tasks
    for i in td.API.state['items']:
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

    render_output_table(output_table.items(), project, project_table)
