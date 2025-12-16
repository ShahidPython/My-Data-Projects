import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(SCRIPT_DIR, 'tasks.json')

def show_menu():
    """Show the main menu options"""
    print("\n=== To-Do List ===")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Mark Task Done")
    print("4. Delete Task")
    print("5. Quit")

def get_tasks():
    """Load tasks from file, return empty list if file doesn't exist"""
    if os.path.exists('tasks.json'):
        try:
            with open('tasks.json', 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_tasks(tasks):
    """Save tasks to file"""
    with open('tasks.json', 'w') as f:
        json.dump(tasks, f, indent=2)

def print_tasks(tasks):
    """Display all tasks with their status"""
    if not tasks:
        print("No tasks yet!")
        return
    
    print("\nYour Tasks:")
    for i, task in enumerate(tasks, 1):
        status = "✓" if task['done'] else "✗"
        print(f"{i}. [{status}] {task['name']}")

def get_task_number(max_num):
    """Get valid task number from user"""
    while True:
        try:
            num = int(input("Enter task number: "))
            if 1 <= num <= max_num:
                return num
            print(f"Please enter 1-{max_num}")
        except ValueError:
            print("Numbers only please")

def main():
    """Run the to-do list app"""
    tasks = get_tasks()
    
    while True:
        show_menu()
        choice = input("Choose (1-5): ").strip()
        
        if choice == '1':
            name = input("Task name: ").strip()
            if name:
                tasks.append({'name': name, 'done': False})
                save_tasks(tasks)
                print(f"Added '{name}'")
            else:
                print("Task can't be empty!")
                
        elif choice == '2':
            print_tasks(tasks)
            
        elif choice == '3':
            print_tasks(tasks)
            if tasks:
                num = get_task_number(len(tasks))
                tasks[num-1]['done'] = True
                save_tasks(tasks)
                print("Marked as done!")
                
        elif choice == '4':
            print_tasks(tasks)
            if tasks:
                num = get_task_number(len(tasks))
                removed = tasks.pop(num-1)
                save_tasks(tasks)
                print(f"Deleted '{removed['name']}'")
                
        elif choice == '5':
            print("See you later!")
            break
            
        else:
            print("Please choose 1-5")

if __name__ == '__main__':
    main()