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


def add_task(description):
    tasks = load_tasks()
    task = {
        'id': generate_id(tasks),
        'description': description,
        'status': "todo",
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
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


def main():
    parser = argparse.ArgumentParser(description="Simple task tracker")
    subparsers = parser.add_subparsers(dest='command')

    # add
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('description', nargs='+', help='Task description')

    # update: allow either a new description (positional) and/or --status
    update_parser = subparsers.add_parser('update', help='Update a task')
    update_parser.add_argument('id', type=int, help='Task id')
    update_parser.add_argument('description', nargs='*', help='New description (multi-word allowed)')
    update_parser.add_argument('--status', choices=['todo', 'in-progress', 'done'], help='New status')

    # delete
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('id', type=int, help='Task id')

    # list (optional status filter)
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('status', nargs='?', choices=['todo', 'in-progress', 'done'], help='Filter by status')

    # mark-in-progress / mark-done convenience commands
    mip_parser = subparsers.add_parser('mark-in-progress', help='Mark a task as in-progress')
    mip_parser.add_argument('id', type=int, help='Task id')

    md_parser = subparsers.add_parser('mark-done', help='Mark a task as done')
    md_parser.add_argument('id', type=int, help='Task id')

    args = parser.parse_args()

    if args.command == 'add':
        description = ' '.join(args.description)
        add_task(description)
    elif args.command == 'update':
        description = None
        if args.description:
            description = ' '.join(args.description)
        update_task(args.id, description=description, status=args.status)
    elif args.command == 'delete':
        delete_task(args.id)
    elif args.command == 'list':
        list_tasks(status=args.status if hasattr(args, 'status') else args.status)
    elif args.command == 'mark-in-progress':
        update_task(args.id, status='in-progress')
    elif args.command == 'mark-done':
        update_task(args.id, status='done')
    else:
        parser.print_help()


if __name__ == '__main__':
    main()