"""Functions for rendering"""

import logging
import operator
from typing import ItemsView

from tabulate import tabulate

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

def render_output_table(items: ItemsView, project, project_table) -> None:
    """Construct and print pretty table"""
    for i, data in items:

        # for specified prject skip if not correct
        if project and project != project_table[i]:
            continue
        try:
            values = sorted(data, key=operator.itemgetter('sys_date', 'priority'))
            output_values = [map(lambda x: print_colored(x, i['priority']),
                                 ['{:x}'.format(i['id']), i['due_date'], i['content'],
                                  i.get('labels', "")]) for i in values]
            if output_values:
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
