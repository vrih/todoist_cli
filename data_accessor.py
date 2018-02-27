"""Functions for returning data objects from todoist"""
# global var
API = None

def lookup_table(key, value, data):
    output = {}
    for i in API.state[data]:
        try:
            output[i[key]] = i[value]
        except:
            continue

    return output

def note_ids():
    return lookup_table('item_id', 'id', 'notes')

def notes(task):
    """Return notes for task"""
    return [i for i in API.state['notes'] if i['item_id'] == task]

def project_ids():
    return lookup_table('id', 'name', 'projects')

def project_names():
    return lookup_table('name', 'id', 'projects')


def label_names():
    return lookup_table('name', 'id', 'labels')


def label_ids():
    return lookup_table('id', 'name', 'labels')


def task_ids():
    return lookup_table('id', 'content', 'items')



def incomplete_task_ids():
    tasks = lookup_table('id', 'checked', 'items')
    output = []
    for item, checked in tasks.items():
        try:
            if checked != 1:
                output.append(f"{item:x}")
        except Exception:
            continue
    return output
