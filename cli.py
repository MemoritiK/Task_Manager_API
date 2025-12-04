import curses
import requests
from datetime import date

BASE_URL = "http://127.0.0.1:8000"  # FastAPI backend URL

def fetch_tasks():
    r = requests.get(f"{BASE_URL}/tasks/")
    tasks = r.json()
    # Sort: completed tasks go to the end
    tasks.sort(key=lambda t: t["status"] == "completed")
    return tasks

def add_task(name, priority):
    today = date.today()
    date_created = today.strftime("%b %-d")  # e.g., 'Jan 2'
    data = {"name": name, "priority": priority, "date": date_created}
    requests.post(f"{BASE_URL}/tasks/", json=data)

def update_task(task_id, name=None, priority=None, status=None):
    data = {}
    if name is not None:
        data["name"] = name
    if priority is not None:
        data["priority"] = priority
    if status is not None:
        data["status"] = status
    if data:
        requests.put(f"{BASE_URL}/tasks/{task_id}", json=data)

def delete_task(task_id):
    requests.delete(f"{BASE_URL}/tasks/{task_id}")

def get_input(stdscr, prompt):
    curses.echo()
    height, width = stdscr.getmaxyx()
    stdscr.move(height - 2, 0)
    stdscr.clrtoeol()
    stdscr.addstr(height - 2, 0, prompt)
    stdscr.refresh()
    user_input = stdscr.getstr(height - 2, len(prompt)).decode()
    curses.noecho()
    return user_input.strip()

def main(stdscr):
    # Initialize curses
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # High priority red

    cursor = 0
    offset = 0

    while True:
        stdscr.clear()
        tasks = fetch_tasks()
        num_tasks = len(tasks)
        height, width = stdscr.getmaxyx()
        display_height = height - 6  # title + instructions + input line

        # Title
        stdscr.addstr(0, 0, "Task Manager", curses.A_BOLD | curses.A_UNDERLINE)
        # Instructions
        stdscr.addstr(2, 0, "a=Add  u=Update  Space=Complete  Del=Delete  ↑/↓=Navigate  q=Quit")

        # Adjust scrolling
        if cursor < offset:
            offset = cursor
        elif cursor >= offset + display_height:
            offset = cursor - display_height + 1

        # Display tasks
        for idx in range(offset, min(offset + display_height, num_tasks)):
            task = tasks[idx]
            checkbox = "[x]" if task["status"] == "completed" else "[ ]"
            line = f"{checkbox} {task['name']:<20} {task['priority']:<6} {task['date']:<6}"
            line_spacing = 2  # number of lines per task
            y = 4 + (idx - offset) * line_spacing

            # Set attributes
            attr = curses.A_REVERSE if idx == cursor else curses.A_NORMAL
            if task["priority"] == "High":
                attr |= curses.color_pair(1)
            if task["status"] == "completed":
                attr |= curses.A_DIM

            stdscr.addstr(y, 0, line[:width - 1], attr)

        stdscr.refresh()
        k = stdscr.getch()

        # Navigation
        if k == curses.KEY_UP and cursor > 0:
            cursor -= 1
        elif k == curses.KEY_DOWN and cursor < num_tasks - 1:
            cursor += 1
        elif k == ord("q"):
            break
        elif k == ord(" "):  # mark completed
            if tasks:
                task = tasks[cursor]
                if task["status"] != "completed":
                    update_task(task["id"], status="completed")
                if cursor < len(tasks) - 1:
                    cursor += 1
        elif k == curses.KEY_DC:  # delete key
            if tasks:
                delete_task(tasks[cursor]["id"])
                if cursor >= len(tasks) - 1 and cursor > 0:
                    cursor -= 1
        elif k == ord("a"):  # add task
            name = get_input(stdscr, "Enter task name: ")
            while True:
                prio_input = get_input(stdscr, "Priority? [n]ormal/[h]igh: ").upper()
                if prio_input in ["N", "H"]:
                    priority = "Normal" if prio_input == "N" else "High"
                    break
            add_task(name, priority)
        elif k == ord("u"):  # update task
            if tasks:
                task = tasks[cursor]

                # Update name
                name = get_input(stdscr, f"Update name ({task['name']}): ")
                if not name:
                    name = None  # no change

                # Update priority
                while True:
                    prio_input = get_input(
                        stdscr,
                        f"Update priority ({task['priority']})? [n]ormal/[h]igh/[Enter]=no change: "
                    ).upper()
                    if prio_input in ["N", "H"]:
                        priority = "Normal" if prio_input == "N" else "High"
                        break
                    elif prio_input == "":
                        priority = None
                        break

                update_task(task["id"], name=name, priority=priority)
curses.wrapper(main)