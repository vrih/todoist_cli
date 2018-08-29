#!/usr/bin/env python3
"""CLI for todoist"""
import argparse
from typing import List, Dict

import data_accessor as da
import interactive
import renderer as rd
import todoist_calls as td

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

if __name__ == "__main__":
    ARGS = arg_parser()

    da.API = td.API

    OUTPUT_TABLE: Dict = {}

    TASKS: List[int] = []

    if ARGS.task:
        TASKS = [int(task, 16) for task in ARGS.task]

    if ARGS.command == "interactive":
        interactive.interactive()
    elif ARGS.command == "list":
        rd.print_all_tasks(project=ARGS.project, date=ARGS.date)
    elif ARGS.command == "complete":
        if TASKS:
            td.complete_task(TASKS)
    elif ARGS.command == "delete":
        if TASKS:
            td.delete_task(TASKS)
    elif ARGS.command == "add":
        td.add_task(ARGS.content, ARGS.project, ARGS.date, ARGS.labels, ARGS.priority)
    elif ARGS.command == "update":
        td.update_task(TASKS, ARGS.date, ARGS.content, ARGS.labels, ARGS.priority)
