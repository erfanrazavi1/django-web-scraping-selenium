import subprocess
import os
import sys
import signal
import time

server_process = None  

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(os.path.dirname(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def start_server():
    global server_process
    if server_process is None:
        print(f"Starting Django server in: {BASE_DIR}")
        server_process = subprocess.Popen(
            ["python", "core/manage.py", "runserver"], 
            cwd=BASE_DIR,
            shell=True
        )
        time.sleep(2)  
        print("Server started!")
    else:
        print("Server is already running.")

def stop_server():
    global server_process
    if server_process:
        print("Stopping Django server...")
        os.kill(server_process.pid, signal.SIGTERM)
        server_process = None
        print("Server stopped!")
    else:
        print("Server is not running.")

if __name__ == "__main__":
    while True:
        command = input("Enter 'start' to run server, 'stop' to kill it, 'exit' to quit: ").strip().lower()
        if command == "start":
            start_server()
        elif command == "stop":
            stop_server()
        elif command == "exit":
            if server_process:
                stop_server()
            break
        else:
            print("Invalid command! Use 'start', 'stop', or 'exit'.")
