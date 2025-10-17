import argparse
import os
import json
from datetime import datetime

TASK_FILE = 'tasks.json'


def load_tasks():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, 'r') as file:
            return json.load(file)
    return []


def save_tasks(tasks):
    with open(TASK_FILE, 'w') as file:
        json.dump(tasks, file, indent=4)


def generate_id(tasks):
    if tasks:
        return max(task['id'] for task in tasks) + 1
    return 1


# ==========================
# Task Management Functions
# ==========================

ts = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

def add_task(description):
    tasks = load_tasks()
    task = {
        'id': generate_id(tasks),
        'description': description,
        'status': "todo",
        'created_at': ts,
        'updated_at': ts
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"Task added successfully (ID: {task['id']})")


def update_task(task_id, description=None, status=None):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            changed = False
            if description:
                task['description'] = description
                changed = True
            if status:
                task['status'] = status
                changed = True
            if changed:
                task['updated_at'] = datetime.now().isoformat()
                save_tasks(tasks)
                print(f"Task {task_id} updated.")
            else:
                print("No changes provided.")
            return
    print(f"Task {task_id} not found.")


def delete_task(task_id):
    tasks = load_tasks()
    before = len(tasks)
    tasks = [task for task in tasks if task['id'] != task_id]
    if len(tasks) == before:
        print(f"Task {task_id} not found.")
        return
    save_tasks(tasks)
    print(f"Task {task_id} deleted.")


def list_tasks(status=None):
    tasks = load_tasks()
    if status:
        tasks = [task for task in tasks if task['status'] == status]
    if not tasks:
        print("No tasks found.")
        return
    for task in tasks:
        print(f"{task['id']}: {task['description']} [{task['status']}] (Created: {task['created_at']}, Updated: {task['updated_at']})")

'''
Argument Parser
|
|__subparsers
   |__add_parser('add')
        |__add_argument('descriptions')

   |__add_parser('update')
        |__add_argument('id')
        |__add_argument('descriptions')
        |__add_argument('status')

   |__add_parser('delete')
        |__add_argument('id')

   |__add_parser('list')
        |__add_argument('status')

   |__add_parser('mark-in-progress')
        |__add_argument('id')

   |__add_parser('mark-done')
        |__add_argument('id')

'''
def main():
    parser = argparse.ArgumentParser(description="Simple task tracker")
    subparsers = parser.add_subparsers(dest='command')

    # add
    add_parser = subparsers.add_parser('add', help='Add a new task')
        #descriptions: list of words -> nargs = number arguments
        # '*': 0 - many
        # '+': 1 - many
        # '?': 0 - 1
        # 1: 1
    add_parser.add_argument('description', nargs='+', help='Task description')

    # Update Task
    parser_update = subparsers.add_parser('update', help= 'Update on existing task')
    parser_update.add_argument('id', type=int, help='ID of the task to update')
    parser_update.add_argument('--descriptions', nargs='*', help='New description of the task')
    parser_update.add_argument('--status',type=str, choices=['todo', 'in-progress', 'done'], help='New status for the task')

    # Delete Task
    parser_delete = subparsers.add_parser('delete', help = 'Delete a task')
    parser_delete.add_argument('id', type=int, help='ID of the task to delete')

    # List Tasks
    parser_list = subparsers.add_parser('list', help='List all tasks')
    parser_list.add_argument('--status', type=str, choices=['todo', 'in-progress', 'done'], help='Filter tasks by status')

    # Mark In-Progress
    parser_mark_in_progress = subparsers.add_parser('mark-in-progress', help='Mark a task as in-progress')
    parser_mark_in_progress.add_argument('id', type=int, help='ID of the task to mark as in-progress')

    # Mark Done
    parser_mark_done = subparsers.add_parser('mark-done', help='Mark a task as done')
    parser_mark_done.add_argument('id', type=int, help='ID of the task to mark as done')    

    args = parser.parse_args()

    if(args.command == 'add'):
        #Join list of words to a single string
        description = ' '.join(args.description)
        add_task(description)
    elif(args.command == 'update'):
        description = ' '.join(args.description) if args.description else None
        update_task(args.id, description=description, status=args.status)
    elif(args.command == 'delete'):
        delete_task(args.id)
    elif(args.command == 'list'):
        #Check if args.status exists
        list_tasks(status=args.status if hasattr(args, 'status') else None)
    elif(args.command == 'mark-in-progress'):
        update_task(args.id, status='in-progress')
    elif(args.command == 'mark-done'):
        update_task(args.id, status='done')
    else:
        parser.print_help()


if __name__ == '__main__':
    main()