import os
import random
import psutil
import time
import subprocess
import pandas as pd
import argparse
import threading
import winreg
import shutil
import json
import sqlite3

source_file = r"C:\Windows\System32\calc.exe" 
directory = r"D:\test"
service_name = "Agent_Hunting"
display_name = "Hunting"
exe_path = r"D:\My Project\Agent_Hunting\Agent.exe"
db_path = r'D:\My Project\Agent_Hunting\data.db'
output_file = "result.xlsx"
base_key = winreg.HKEY_LOCAL_MACHINE
sub_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

operations = {
    'Create File': 'create_files',
    'Read File': 'read_files',
    'Delete File': 'delete_files',
    'Write File': 'write_files',
    'Create Process': 'create_processes',
    'Terminate Process': 'terminate_processes',
    'Create Registry': 'add_registry',
    'Edit Registry': 'edit_registry',
    'Delete Registry': 'delete_registry'
}

def measure_cpu_ram_usage(interval=1, duration=5):
    """
    Measure average CPU and RAM usage over a specified duration.

    Args:
        interval (int): Interval in seconds between measurements.
        duration (int): Duration in seconds to measure CPU and RAM usage.

    Returns:
        tuple: Average CPU usage percentage and RAM usage percentage.
    """
    usage_samples_cpu = []
    usage_samples_ram = []

    for _ in range(duration):
        usage_samples_cpu.append(psutil.cpu_percent(interval=interval))
        usage_samples_ram.append(psutil.virtual_memory().percent)

    avg_usage_cpu = sum(usage_samples_cpu) / len(usage_samples_cpu)
    avg_usage_ram = sum(usage_samples_ram) / len(usage_samples_ram)

    return avg_usage_cpu, avg_usage_ram

# Open file
def create_files(destination_folder, num_files,num_run):

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    buffer = None
    with open(source_file,'rb') as src:
        buffer = src.read()
    
    # Copy file 100 lần
    try:
        for i in range(1, num_files):
            destination_file = os.path.join(destination_folder, f"file_{i}_{num_run}.exe")
            with open(destination_file,'wb') as src:
                src.write(buffer)
            # shutil.copy(source_file, destination_file)
            time.sleep(0.1)
    except Exception as e:
        print(f"Lỗi khi copy file: {e}")

# Read file
def read_files(directory, num_):
    exe_files = [f for f in os.listdir(directory) if f.endswith('.exe')]    
    exe_files_to_delete = exe_files[:num_]        
    try:
        for file in exe_files:
            buffer = None
            file_path = os.path.join(directory, file)
            with open(file_path,'rb') as src:
                buffer = src.read()
                time.sleep(0.1)
                # time.sleep(0.1)
        
        # for i in range(0, num_):
        #     with open(source_file,'rb') as src:
        #         buffer = src.read()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
        #         print(f'Read file {source_file}')
        #     time.sleep(0.1)       
    except Exception as e:
        print(f'Exception read files: {e}')
        
#Write file
def write_files(directory, num_files):
    if not os.path.exists(directory):
        os.makedirs(directory)

    if not os.path.exists(source_file):
        raise FileNotFoundError(f"The source file '{source_file}' does not exist.")
    
    buffer = None
    with open(source_file, "rb") as src: 
        buffer = src.read()
    for i in range(1, num_files + 1):
        file_name = os.path.join(directory, f"file_{i}.exe")
        with open(file_name, "wb") as dst:
            dst.write(buffer)
        time.sleep(0.1)
        
#Delete file
def delete_files(directory,num_):

    try:
        # Check if the directory exists
        if not os.path.exists(directory):
            print(f"The directory '{directory}' does not exist.")
            return
        # Get a list of .exe files in the directory
        exe_files = [f for f in os.listdir(directory) if f.endswith('.exe')]
        exe_files_to_delete = exe_files[:num_]
                
        if not exe_files_to_delete:
            print("No .exe files found to delete.")
            return

        for file in exe_files_to_delete:
            file_path = os.path.join(directory, file)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting '{file_path}': {e}") 
            time.sleep(0.1)  
    except Exception as e:
        print(f"Error: {e}")
        
#Process function
#Create process
def create_processes(num_processes):

    threads = []
    def run_file(source_file):
         subprocess.run(["cmd", "/c", source_file], check=True)

    for i in range(0, num_processes):
        try:
            # Create a thread to monitor the process
            thread = threading.Thread(target=run_file, args=(source_file,))
            threads.append(thread)
            thread.start()            
        except Exception as e:
            print(f"Error starting process {i + 1}: {e}")

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

# Terminate processes
def terminate_processes(process_name):

    try:
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            if proc.info['name'] == process_name:
                subprocess.run(["taskkill", "/PID", str(proc.info['pid']), "/F"], stdout=subprocess.DEVNULL, check=True, shell=True)
            # time.sleep(0.1)
    except Exception as e:
        print(f"Error terminating processes: {e}")
        
#Function registry 
def add_registry(num_keys):
    try:
        with winreg.OpenKey(base_key, sub_key, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            for i in range(1, num_keys + 1):
                value_name = f"Key_{i}"
                value_data = f"Value_{i}"
                winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value_data)
    except Exception as e:
        print(f"Error adding registry keys: {e}")
        
def edit_registry(num_key,num_run):

    try:
        with winreg.OpenKey(base_key, sub_key, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            i = 0
            while i < num_key:
                try:
                    value_name, value_data, value_type = winreg.EnumValue(key, i)
                    if value_name.startswith('Key'):
                        new_value_data = f"Edited_{num_run}_{value_data}" 
                        winreg.SetValueEx(key, value_name, 0, value_type, new_value_data)
                    i += 1
                except OSError:
                    break
    except Exception as e:
        print(f"Error editing registry values: {e}")

def delete_registry(num_key):
    try:
        with winreg.OpenKey(base_key, sub_key, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            i = 0
            while i < num_key:
                try:
                    # Enumerate values
                    value_name, value_data, value_type = winreg.EnumValue(key, i)
                    if value_name.startswith('Key'):
                        winreg.DeleteValue(key, value_name)
                    else:
                        i += 1
                except OSError:
                    break
    except PermissionError:
        print("Permission denied. Run the script with Administrator privileges.")
    except Exception as e:
        print(f"Error deleting registry values: {e}")


def count_event(db_path, file_directory=r'D:\Test', registry_directory='HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run'):
    # Kết nối tới cơ sở dữ liệu SQLite
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        sqlCommand = f"""
        SELECT OBject, Action FROM Config
        """
        cursor.execute(sqlCommand)
        operations = {}

        for line in cursor:
            if line == ('Registry', 'Add'):
                operations['Create Registry'] = 0
            else:
                event_name = f'{line[1]} {line[0]}'
                operations[event_name] = 0 

        if operations:
            for key, value in operations.items():

                sqlCommand = f"""
                SELECT * FROM Logs WHERE NAME="{key}"
                """
                cursor.execute(sqlCommand)
                data = cursor.fetchall()

                file_names = set()
                # print(data)
                for row in data:
                    json_data = json.loads(row[3])  
                    action, object = row[1].split(' ')
                    if object == 'File':
                        file_path = json_data.get("fields", {}).get("file_path", "")
                        file_name = json_data.get("fields",{}).get("file_name","")
                        # print(f'File path: {file_path} - File name: {file_name}')
                        if file_path.startswith(file_directory) and file_name.endswith('.exe'): 
                            operations[f'{action} {object}'] +=1
                    elif object == 'Process':
                        cmd_line = json_data.get("fields", {}).get("command_line", "")
                        if cmd_line.endswith('calc.exe'):
                            operations[f'{action} {object}'] +=1
                    elif object == 'Registry':
                        image_path = json_data.get("fields", {}).get("image_path", "")
                        key = json_data.get("fields", {}).get("key", "")
                        print(f'Image={image_path}, Key={key}')
                        if image_path.endswith('python.exe') and key == registry_directory:
                            operations[f'{action} {object}'] +=1
        # delete_logs_query = "DELETE FROM Logs"
        # cursor.execute(delete_logs_query)
        # conn.commit()   
        return operations
        
# Append data measure to file excel
def append_to_excel(file_name, data):

    try:
        if os.path.exists(file_name):
            existing_df = pd.read_excel(file_name, engine='openpyxl')
            new_df = pd.DataFrame(data)
            result_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            result_df = pd.DataFrame(data)
        result_df.to_excel(file_name, index=False, engine='openpyxl')
    except PermissionError:
        raise PermissionError(f"Cannot write to file '{file_name}'")

def manage_service(action, service_name, exe_path):
    if action == "install":
        # result = subprocess.run(
        #     ["sc.exe", "query", service_name],
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     text=True
        # )
        result = [service for service in psutil.win_service_iter() if service.name() == service_name]
        if result:
            print('Service installed')
        else:
            # Corrected syntax for sc.exe create
            subprocess.run([
                "sc.exe", "create", service_name,
                f'binPath="{os.path.abspath(exe_path)}',
                "start=auto"
            ], check=True)

            # Set display name separately if provided
            if display_name:
                subprocess.run([
                    "sc.exe", "config", service_name,
                    f'DisplayName={display_name}'
                ], check=True)
    elif action == "start":
        subprocess.run(["sc.exe", "start", service_name], check=True)
    elif action == "stop":
        subprocess.run(["sc.exe", "stop", service_name], check=True)
    elif action == "delete":
        subprocess.run(["sc.exe", "delete", service_name], check=True)
    time.sleep(30)

def start_task(operation_, *args):
    
    if not os.path.exists(exe_path):
        raise FileNotFoundError(f"The file '{exe_path}' does not exist.")

    # Measure before running service
    cpu_before, ram_before = measure_cpu_ram_usage(duration=5)
    # Start agent as service
    # manage_service("install", service_name, exe_path)
    manage_service("start", service_name, exe_path)
    # Create thread to measure CPU/RAM usage
    thread_measure = threading.Thread(target=measure_cpu_ram_usage, args=(1,5))
    try:
        thread_measure.start()
        operation_(*args)
        cpu_after, ram_after = measure_cpu_ram_usage()
        thread_measure.join()
        manage_service("stop", service_name, exe_path)
        
    except Exception as e:
        print(f"Error during task execution: {e}")
    finally:
         # Append results to Excel
        return cpu_before, cpu_after, ram_before, ram_after
        


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Test case")
    # parser.add_argument("--operation", type=str, help="Function for executing: [read_files,create_files,write_files,delete_files,create_processes,terminate_processes,add_registry,edit_registry,delete_registry]")
    # parser.add_argument("--directory", type=str, help="Directory to create files in.")
    # parser.add_argument("--num_files", type=int,  help="Number of files to create.")
    # parser.add_argument("--num_process", type=int, help="Number of process to create.")
    # parser.add_argument("--process_name", type=str, help="Name of processes to terminate.")
    # parser.add_argument("--num_key_registry", type=int, help="Number of key to add registry.")
    # parser.add_argument("--num_run", type=int, help="Number of round measure")
    
    # args = parser.parse_args()
    # count_num = None
    # try:
    #     for i in range(1, args.num_run+1):
    #         if args.operation == 'read_files':
    #             write_files(args.directory,args.num_files)
    #             time.sleep(30)
    #             # shutil.copy(source_file, r'D:\Test\calc.exe')
    #             count_num = args.num_files
    #             cpu_before, cpu_after, ram_before, ram_after= start_task(read_files,args.directory,args.num_files)
    #             delete_files(args.directory,args.num_files)
    #             # os.remove(r'D:\Test\calc.exe')      # print(f'Read file {file_path}')

    #         elif args.operation == 'create_files':
    #             count_num = args.num_files
    #             cpu_before, cpu_after, ram_before, ram_after= start_task(create_files,args.directory,args.num_files,i)
    #             delete_files(args.directory,args.num_files)
    #         elif args.operation == 'write_files':
    #             count_num = args.num_files
    #             cpu_before, cpu_after, ram_before, ram_after= start_task(write_files,args.directory,args.num_files)
    #             delete_files(args.directory,args.num_files)
    #         elif args.operation == 'delete_files':
    #             write_files(args.directory,args.num_files)
    #             time.sleep(30)
    #             count_num = args.num_files
    #             cpu_before, cpu_after, ram_before, ram_after= start_task(delete_files,args.directory,args.num_files)
    #         elif args.operation == 'create_processes':
    #             count_num = args.num_process
    #             cpu_before, cpu_after, ram_before, ram_after= start_task(create_processes,args.num_process)
    #             terminate_processes('CalculatorApp.exe')
    #         elif args.operation == 'terminate_processes':
    #             count_num = args.num_process
    #             create_processes(args.num_process)
    #             time.sleep(30)
    #             cpu_before, cpu_after, ram_before, ram_after= start_task(terminate_processes,args.num_process,args.process_name)
    #         elif args.operation == 'add_registry':
    #             count_num = args.num_key_registry
    #             cpu_before, cpu_after, ram_before, ram_after= start_task(add_registry,args.num_key_registry)
    #             delete_registry(args.num_key_registry)
    #         elif args.operation == 'edit_registry':
    #             add_registry(args.num_key_registry)
    #             time.sleep(30)
    #             count_num = args.num_key_registry
    #             cpu_before, cpu_after, ram_before, ram_after= start_task(edit_registry,args.num_key_registry,i)
    #             delete_registry(args.num_key_registry)
    #         elif args.operation == 'delete_registry':
    #             add_registry(args.num_key_registry)
    #             count_num = args.num_key_registry
    #             time.sleep(30)
    #             cpu_before, cpu_after, ram_before, ram_after= start_task(delete_registry,args.num_key_registry)
    #             delete_registry(args.num_key_registry)
    #         count_array= count_event(db_path,file_directory=args.directory)
    #         action = [key for key, value in operations.items() if value == args.operation][0] 
    #         data = {
    #             "Action": [action], 
    #             "CPU Before": [cpu_before],
    #             "CPU After": [cpu_after],
    #             "RAM Before": [ram_before],
    #             "RAM After": [ram_after],
    #             "Count event": [count_num],
    #             "Count event measure": [count_array[action]]
    #         }
    #         append_to_excel(output_file, data)
    #         time.sleep(20)    
    # except Exception as e:
    #     print(f"Error: {str(e)}")
    
    create_files(r'D:\test',100,1)
    # print(count_event(db_path))
    # write_files(r'D:\test', 100)
    # create_processes(20)
    # terminate_processes('CalculatorApp.exe')
    # write_files(r'D:\test', 100)
    # write_files(r'D:\test',100)

    # cpu_before, cpu_after, ram_before, ram_after = start_task(write_files,r'D:\test',100)
    # write_files(r'D:\Test',50)
    # delete_files(r'D:\Test',50)
    #  subprocess.run([
    #             "sc.exe", "create", service_name,
    #             f'binPath="{os.path.abspath(exe_path)}',
    #             "start=auto"
    #         ], check=True)
    #  subprocess.run([
    #                 "sc.exe", "config", service_name,
    #                 'type=interact'
    #             ], check=True)
    # create_processes(5)
    # terminate_processes('CalculatorApp.exe')
    # delete_registry()