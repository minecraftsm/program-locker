import psutil
import subprocess
import threading
import sys
import time
import tkinter as tk
from tkinter import simpledialog

# 定义密码
password = "minecraft20111025"

# 定义用于监视的进程名称
process_name = "WeChat.exe"


# 结束目标进程的函数
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


# 结束目标进程
def end_process(process):
    try:
        process.terminate()
        process.wait(timeout=1)
    except (psutil.NoSuchProcess, AttributeError, psutil.Error, OSError):
        pass


# 启动新程序
def start_new_program(program_path):
    subprocess.Popen(program_path)
    sys.exit()


# 检查密码是否正确
def check_password():
    global wrong_password_count, stop_prompt, should_exit
    if stop_prompt:  # 如果标志为 True，不再弹出密码输入窗口
        return False
    entered_password = prompt_for_password()
    if entered_password == password:
        print("Password correct. Starting new program.")
        start_new_program("C:\\Program Files (x86)\\Tencent\\WeChat\\WeChat.exe")
        should_exit = True  # 设置退出标志
        return True
    else:
        wrong_password_count += 1
        if wrong_password_count >= 10:
            print("Password incorrect. Exiting the program.")
            end_process(get_target_process())  # 在密码错误达到十次时结束微信进程
            time.sleep(1)
            if not is_process_running(process_name):
                stop_thread = True
                stop_prompt = True  # 达到十次错误输入后停止弹窗
                should_exit = True  # 设置退出标志
        else:
            print("Incorrect password. Please try again.")
    return False


# 监视目标进程的线程函数
def monitor_process():
    global stop_thread
    while True:
        if is_process_running(process_name):
            print("WeChat.exe is running.")
            stop_thread = False
            end_thread = threading.Thread(target=end_process_loop)
            end_thread.daemon = True  # 设置为守护线程
            end_thread.start()
            while not stop_thread:
                if check_password():
                    stop_thread = True
                time.sleep(1)
            end_thread.join()
        else:
            print("WeChat.exe is not running.")
            time.sleep(1)


# 获取目标进程
def get_target_process():
    try:
        target_processes = [proc for proc in psutil.process_iter(['pid', 'name']) if proc.info['name'] == process_name]
        if target_processes:
            newest_process = max(target_processes, key=lambda x: x.create_time())
            return psutil.Process(newest_process.info['pid'])
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.Error, OSError):
        pass
    return None


# 检测目标进程是否运行
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
should_exit = False  # 用于指示程序是否应该退出

# 启动监视线程
monitor_thread = threading.Thread(target=monitor_process)
monitor_thread.start()


# 弹出式输入密码窗口
def prompt_for_password():
    root = tk.Tk()
    root.withdraw()
    entered_password = simpledialog.askstring("Password", "Please enter the password:", show="*")
    root.destroy()
    return entered_password


# 等待监视线程结束
monitor_thread.join()
