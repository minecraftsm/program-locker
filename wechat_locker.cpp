#include <iostream>
#include <string>
#include <windows.h>
#include <tlhelp32.h>

using namespace std;

// ��������ͽ�������
const string password = "minecraft20111025";
const string process_name = "WeChat.exe";

// ȫ�ֱ���
bool stop_thread = false;
int wrong_password_count = 0;
bool stop_prompt = false;
bool should_exit = false;
bool enter_infinite_loop = false; // ��־����ʾ�Ƿ����������ѭ���ر�΢�Ž��̵�ģʽ

// ��������
DWORD WINAPI end_process_loop(LPVOID lpParam);
void end_process(HANDLE process_handle);
bool check_password();
void start_new_program(const string& program_path);
DWORD WINAPI monitor_process(LPVOID lpParam);
HANDLE get_target_process();
bool is_process_running(const string& process_name);
string prompt_for_password();

int main() {
    HANDLE monitor_thread_handle = CreateThread(NULL, 0, monitor_process, NULL, 0, NULL);
    WaitForSingleObject(monitor_thread_handle, INFINITE);
    CloseHandle(monitor_thread_handle);
    return 0;
}

DWORD WINAPI end_process_loop(LPVOID lpParam) {
    while (!stop_thread) {
        HANDLE process_handle = get_target_process();
        if (process_handle != NULL) {
            end_process(process_handle);
        }
        Sleep(1000);
    }
    return 0;
}

void end_process(HANDLE process_handle) {
    TerminateProcess(process_handle, 0);
    CloseHandle(process_handle);
}

bool check_password() {
    if (stop_prompt) {
        return false;
    }
    string entered_password = prompt_for_password();
    if (entered_password == password) {
        cout << "Password correct. Starting new program." << endl;
        start_new_program("C:\\Program Files (x86)\\Tencent\\WeChat\\WeChat.exe");
        should_exit = true;
        return true;
    } else {
        wrong_password_count++;
        if (wrong_password_count >= 10) {
            cout << "Password incorrect more than ten times. Entering infinite loop to end WeChat process." << endl;
            stop_thread = true;
            stop_prompt = true;
            enter_infinite_loop = true; // ���ñ�־��ʾ����������ѭ���ر�΢�Ž��̵�ģʽ

        } else {
            cout << "Incorrect password. Please try again." << endl;
        }
        return false;
    }
}

void start_new_program(const string& program_path) {
    ShellExecute(NULL, "open", program_path.c_str(), NULL, NULL, SW_SHOWNORMAL);
    exit(0);
}

DWORD WINAPI monitor_process(LPVOID lpParam) {
    while (!should_exit) {
        if (!enter_infinite_loop && is_process_running(process_name)) {
            cout << "WeChat.exe is running." << endl;
            stop_thread = false;
            HANDLE end_thread_handle = CreateThread(NULL, 0, end_process_loop, NULL, 0, NULL);
            while (!stop_thread && !should_exit) {
                if (check_password()) {
                    stop_thread = true;
                }
                Sleep(1000);
            }
            WaitForSingleObject(end_thread_handle, INFINITE);
            CloseHandle(end_thread_handle);
        } else if (enter_infinite_loop) { // �������������ѭ���ر�΢�Ž��̵�ģʽ
            cout << "Entering infinite loop to end WeChat process." << endl;
            while (is_process_running(process_name)) {
                HANDLE process_handle = get_target_process();
                if (process_handle != NULL) {
                    end_process(process_handle);
                }
                Sleep(1000);
            }
            enter_infinite_loop = false; // �˳�����ѭ���ر�΢�Ž��̵�ģʽ
            wrong_password_count = 0; // ��������������
            should_exit = false; // �����˳���־���Ա�������΢�Ž���
        } else {
            cout << "WeChat.exe is not running." << endl;
            Sleep(1000);
        }
    }
    return 0;
}

HANDLE get_target_process() {
    HANDLE hProcessSnap;
    PROCESSENTRY32 pe32;

    hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hProcessSnap == INVALID_HANDLE_VALUE) {
        return NULL;
    }

    pe32.dwSize = sizeof(PROCESSENTRY32);

    if (!Process32First(hProcessSnap, &pe32)) {
        CloseHandle(hProcessSnap);
        return NULL;
    }

    HANDLE process_handle = NULL;
    do {
        if (string(pe32.szExeFile) == process_name) {
            process_handle = OpenProcess(PROCESS_TERMINATE, FALSE, pe32.th32ProcessID);
            break;
        }
    } while (Process32Next(hProcessSnap, &pe32));

    CloseHandle(hProcessSnap);
    return process_handle;
}

bool is_process_running(const string& process_name) {
    HANDLE hProcessSnap;
    PROCESSENTRY32 pe32;

    hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hProcessSnap == INVALID_HANDLE_VALUE) {
        return false;
    }

    pe32.dwSize = sizeof(PROCESSENTRY32);

    if (!Process32First(hProcessSnap, &pe32)) {
        CloseHandle(hProcessSnap);
        return false;
    }

    bool is_running = false;
    do {
        if (string(pe32.szExeFile) == process_name) {
            is_running = true;
            break;
        }
    } while (Process32Next(hProcessSnap, &pe32));

    CloseHandle(hProcessSnap);
    return is_running;
}

string prompt_for_password() {
    string entered_password;
    cout << "Please enter the password: ";
    cin >> entered_password;
    return entered_password;
}