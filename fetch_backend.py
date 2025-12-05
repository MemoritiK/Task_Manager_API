import os
import json
from datetime import date
import requests

SESSION_FILE = ".task_manager_session"

def save_session(user):
    """Save logged-in user locally"""
    with open(SESSION_FILE, "w") as f:
        json.dump(user, f)

def load_session():
    """Load logged-in user from local file"""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

BASE_URL = "http://127.0.0.1:8000/users"  # backend URL

def register_user():
    """Register a new user in the backend (does NOT log in)"""
    print("=== Register ===")
    name = input("Username: ").strip()
    password = input("Password: ").strip()
    r = requests.post(f"{BASE_URL}/register/", json={"name": name, "password": password})
    if r.status_code == 200:
        print("User registered successfully!")
    else:
        print("Error:", r.json())
    input("Press Enter to continue...")

def login_user():
    """Login and save user locally"""
    print("=== Login ===")
    name = input("Username: ").strip()
    password = input("Password: ").strip()
    r = requests.post(f"{BASE_URL}/auth/", json={"name": name, "password": password})
    if r.status_code == 200:
        user = r.json()
        save_session(user)
        print(f"Logged in as {user['name']}")
        input("Press Enter to continue...")
        return user
    else:
        print("Login failed:", r.json())
        input("Press Enter to continue...")
        return None

def login_or_register():
    """Show menu until user logs in"""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Welcome to Task Manager CLI!\n")
        print("1. Login")
        print("2. Register")
        print("q. Quit")
        choice = input("Choose option: ").strip()

        if choice == "1":
            user = login_user()
            if user:
                return user
        elif choice == "2":
            register_user()
        elif choice.lower() == "q":
            exit()


BASE_URL_TASKS = "http://127.0.0.1:8000/tasks"

def fetch_tasks(user_id):
    """Get tasks for the current user and sort: unfinished first, then completed"""
    r = requests.get(f"{BASE_URL_TASKS}/")
    tasks = [t for t in r.json() if t.get("user_id") == user_id]
    tasks.sort(key=lambda x: x.get("status") == "completed")
    return tasks

def mark_complete_task(task_id):
    """Toggle task status between 'new' and 'completed'"""
    r = requests.get(f"{BASE_URL_TASKS}/")
    task = next((t for t in r.json() if t["id"] == task_id), None)
    if task:
        new_status = "completed" if task["status"] == "new" else "new"
        requests.put(f"{BASE_URL_TASKS}/{task_id}", json={**task, "status": new_status})

def add_task(name, priority, user_id):
    today = date.today()
    date_created = today.strftime("%b %-d")
    data = {"name": name, "priority": priority, "date": date_created, "status": "new", "user_id": user_id}
    requests.post(f"{BASE_URL_TASKS}/", json=data)

def update_task(task_id, name, priority, user_id):
    today = date.today()
    date_created = today.strftime("%b %-d")
    data = {"name": name, "priority": priority, "date": date_created, "user_id": user_id}
    requests.put(f"{BASE_URL_TASKS}/{task_id}", json=data)

def delete_task(task_id):
    requests.delete(f"{BASE_URL_TASKS}/{task_id}")