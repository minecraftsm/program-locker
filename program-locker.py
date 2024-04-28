import psutil
import subprocess
import threading
import sys
import time
import tkinter as tk
from tkinter import simpledialog

password = "your-password"

process_name = "your-program-name"


def end_process_loop():
    global stop_thread
    while not stop_thread:
        try:
            if is_process_running(process_name):
                process = get_target_process()
                if process:
                    end_process(process)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.Error, OSError):
            pass
        time.sleep(1)


def end_process(process):
    try:
        process.terminate()
        process.wait(timeout=1)
    except (psutil.NoSuchProcess, AttributeError, psutil.Error, OSError):
        pass


def start_new_program(program_path):
    subprocess.Popen(program_path)
    sys.exit()


def check_password():
    global wrong_password_count, stop_prompt, should_exit
    if stop_prompt:
        return False
    entered_password = prompt_for_password()
    if entered_password == password:
        print("Password correct. Starting new program.")
        start_new_program("your-program-location")
        should_exit = True
        return True
    else:
        wrong_password_count += 1
        if wrong_password_count >= 10:  # Fault tolerance number
            print("Password incorrect. Exiting the program.")
            end_process(get_target_process())
            time.sleep(1)
            if not is_process_running(process_name):
                stop_thread = True
                stop_prompt = True
                should_exit = True
        else:
            print("Incorrect password. Please try again.")
    return False


def monitor_process():
    global stop_thread
    while True:
        if is_process_running(process_name):
            print("WeChat.exe is running.")
            stop_thread = False
            end_thread = threading.Thread(target=end_process_loop)
            end_thread.daemon = True
            end_thread.start()
            while not stop_thread:
                if check_password():
                    stop_thread = True
                time.sleep(1)
            end_thread.join()
        else:
            print("WeChat.exe is not running.")
            time.sleep(1)


def get_target_process():
    try:
        target_processes = [proc for proc in psutil.process_iter(['pid', 'name']) if proc.info['name'] == process_name]
        if target_processes:
            newest_process = max(target_processes, key=lambda x: x.create_time())
            return psutil.Process(newest_process.info['pid'])
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.Error, OSError):
        pass
    return None


def is_process_running(process_name):
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == process_name:
                return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.Error, OSError):
        pass
    return False


stop_thread = False
wrong_password_count = 0
stop_prompt = False
should_exit = False

monitor_thread = threading.Thread(target=monitor_process)
monitor_thread.start()


def prompt_for_password():
    root = tk.Tk()
    root.withdraw()
    entered_password = simpledialog.askstring("Password", "Please enter the password:", show="*")
    root.destroy()
    return entered_password


monitor_thread.join()
