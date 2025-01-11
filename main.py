import os
import random
import psutil
import time
import subprocess
import win32serviceutil
import win32service
import win32event
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

def measure_cpu_usage(duration=5):
    """
    Measure average CPU usage over a specified duration.

    Args:
        duration (int): Duration in seconds to measure CPU usage.

    Returns:
        float: Average CPU usage percentage.
    """
    usage_samples = []
    for _ in range(duration):
        usage_samples.append(psutil.cpu_percent(interval=1))
    avg_usage = sum(usage_samples) / len(usage_samples)
    return avg_usage

def measure_ram_usage():
    """
    Measure current RAM usage.

    Returns:
        float: Percentage of RAM used.
    """
    return psutil.virtual_memory().percent

def create_files(directory="output", num_files=100):
    """
    Creates a specified number of files by copying notepad.exe.

    Args:
        directory (str): Directory where files will be created.
        num_files (int): Number of files to create.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    source_file = "notepad.exe"  # File to copy
    if not os.path.exists(source_file):
        raise FileNotFoundError(f"The source file '{source_file}' does not exist.")

    for i in range(1, num_files + 1):
        file_name = os.path.join(directory, f"file_{i}.exe")
        with open(source_file, "rb") as src:
            with open(file_name, "wb") as dst:
                dst.write(src.read())

def append_to_excel(file_name, data):
    """
    Append data to an existing Excel file or create a new one.

    Args:
        file_name (str): Path to the Excel file.
        data (dict): Data to append as a dictionary.
    """
    try:
        if os.path.exists(file_name):
            existing_df = pd.read_excel(file_name, engine='openpyxl')
            new_df = pd.DataFrame(data)
            result_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            result_df = pd.DataFrame(data)
        result_df.to_excel(file_name, index=False, engine='openpyxl')
    except PermissionError:
        raise PermissionError(f"Cannot write to file '{file_name}'. Ensure it is not open in another program.")

def manage_service(action, service_name="AgentService", exe_path="agent.exe"):
    if action == "install":
        subprocess.run([
            "sc", "create", service_name,
            f"binPath= {os.path.abspath(exe_path)}",
            "start= auto"
        ], check=True)
    elif action == "start":
        subprocess.run(["sc", "start", service_name], check=True)
    elif action == "stop":
        subprocess.run(["sc", "stop", service_name], check=True)
    elif action == "delete":
        subprocess.run(["sc", "delete", service_name], check=True)

def start_task(directory, num_files, run_number):
    cpu_before = measure_cpu_usage(duration=5)
    ram_before = measure_ram_usage()

    service_name = "AgentService"
    exe_path = "agent.exe"  # Replace with the correct path to your agent.exe

    if not os.path.exists(exe_path):
        raise FileNotFoundError(f"The file '{exe_path}' does not exist.")

    # Install and start the service
    manage_service("install", service_name, exe_path)
    manage_service("start", service_name)

    try:
        create_files(directory=directory, num_files=num_files)

        cpu_after = measure_cpu_usage(duration=5)
        ram_after = measure_ram_usage()

        # Append results to Excel
        output_file = "result.xlsx"
        data = {
            "Round": [run_number],
            "CPU Before": [cpu_before],
            "CPU After": [cpu_after],
            "RAM Before": [ram_before],
            "RAM After": [ram_after]
        }
        append_to_excel(output_file, data)

        return cpu_before, cpu_after, ram_before, ram_after, output_file
    finally:
        # Stop and delete the service
        manage_service("stop", service_name)
        manage_service("delete", service_name)

def run_gui():
    run_number = 1

    def on_start():
        nonlocal run_number
        try:
            directory = directory_var.get()
            if not directory:
                raise ValueError("Please select a directory.")

            num_files = int(num_files_var.get())
            total_size_gb = int(total_size_var.get())

            # Display and automatically close the "Task Started" message
            task_started_msg = tk.Toplevel(root)
            tk.Label(task_started_msg, text="Task is starting. Please wait...").pack(padx=20, pady=20)
            root.after(2000, task_started_msg.destroy)  # Close after 2 seconds

            # Run the task after the message box closes
            root.after(2000, lambda: run_task(directory, num_files))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_task(directory, num_files):
        nonlocal run_number
        try:
            cpu_before, cpu_after, ram_before, ram_after, output_file = start_task(directory, num_files, run_number)
            run_number += 1

            messagebox.showinfo(
                "Task Complete",
                f"Task completed!\n\nCPU Before: {cpu_before:.2f}%\nCPU After: {cpu_after:.2f}%\n"
                f"RAM Before: {ram_before:.2f}%\nRAM After: {ram_after:.2f}%\n\nResults saved to {output_file}"
            )
        except PermissionError as e:
            messagebox.showerror("File Access Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def select_directory():
        directory = filedialog.askdirectory()
        if directory:
            directory_var.set(directory)

    root = tk.Tk()
    root.title("File Creation Tool")

    tk.Label(root, text="Select Directory:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
    directory_var = tk.StringVar()
    tk.Entry(root, textvariable=directory_var, width=40).grid(row=0, column=1, padx=10, pady=10)
    tk.Button(root, text="Browse", command=select_directory).grid(row=0, column=2, padx=10, pady=10)

    tk.Label(root, text="Number of Files:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
    num_files_var = tk.StringVar(value="100")
    tk.Entry(root, textvariable=num_files_var).grid(row=1, column=1, padx=10, pady=10)

    tk.Label(root, text="Total Size (GB):").grid(row=2, column=0, padx=10, pady=10, sticky="e")
    total_size_var = tk.StringVar(value="1")
    tk.Entry(root, textvariable=total_size_var).grid(row=2, column=1, padx=10, pady=10)

    tk.Button(root, text="Start", command=on_start).grid(row=3, column=0, columnspan=3, pady=20)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
