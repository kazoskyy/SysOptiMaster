import psutil
import GPUtil
import time
import tkinter as tk
import threading
import pystray
from PIL import Image
from tkinter import PhotoImage
from tkinter.ttk import Progressbar

keyboard_blocked = False

def get_cpu_ram_usage():
    try:
        cpu_usage = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        ram_usage = ram.percent
        gpu_usage = get_gpu_usage()
        return cpu_usage, ram_usage, gpu_usage
    except Exception as e:
        return None, None, str(e)

def get_cpu_temperature():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as temp_file:
            temperature = int(temp_file.read()) / 1000  # Convert from millidegrees to degrees
            return f"CPU Temp: {temperature:.2f}°C"
    except FileNotFoundError:
        return "CPU Temp: N/A"  # Temperature file not found
    except PermissionError:
        return "CPU Temp: Permission Denied"
    except Exception as e:
        return f"CPU Temp: Error - {str(e)}"

# GPU
def get_gpu_usage():
    try:
        gpu = GPUtil.getGPUs()[0]
        gpu_usage = gpu.load * 100
        return f"GPU: {gpu_usage:.1f}%"
    except Exception as e:
        return "No GPU"

# Function to get SSD usage (you may need to adjust this to your specific case)
def get_ssd_usage():
    ssd = psutil.disk_usage('/')
    return ssd.percent

def update_info_label():
    while True:
        cpu_usage, ram_usage, gpu_usage = get_cpu_ram_usage()
        usage_text = f"CPU: {cpu_usage:.1f}% | RAM: {ram_usage:.1f}% | {gpu_usage}"
        info_label.config(text=f"{usage_text}\n{get_cpu_temperature()}")
        time.sleep(1)

# Function to update the SSD progress bar
def update_ssd_progress_bar():
    while True:
        ssd_usage = get_ssd_usage()
        ssd_progress_bar['value'] = ssd_usage  # Update the progress bar value
        ssd_label.config(text=f"SSD Usage: {ssd_usage:.1f}%")
        root.update()  # Update the GUI to reflect changes
        time.sleep(1)

def toggle_visibility(event):
    if root.winfo_viewable():
        root.iconify()
    else:
        root.deiconify()

def create_system_tray():
    menu = pystray.Menu(pystray.MenuItem('Open', toggle_visibility))
    image = Image.open('SysOptiMaster-logo.png')
    icon = pystray.Icon('name', image, menu=menu)
    icon.run()
    toggle_visibility(None)

def toggle_keyboard_block():
    global keyboard_blocked
    keyboard_blocked = not keyboard_blocked

def block_keyboard(event):
    if keyboard_blocked:
        return 'break'
    else:
        return None

def update_progress_bars():
    while True:
        cpu_usage, ram_usage, gpu_usage = get_cpu_ram_usage()
        cpu_bar['value'] = cpu_usage
        ram_bar['value'] = ram_usage
        gpu_bar['value'] = gpu_usage
        time.sleep(1)

root = tk.Tk()
root.title("SysOptiMaster-logo.png")
root.attributes('-alpha', 0.7)

# Create a label to display SSD usage
ssd_label = tk.Label(root, text="", font=("Helvetica", 12), justify='left')
ssd_label.pack()

# Create a progress bar for SSD usage
ssd_progress_bar = Progressbar(root, orient="horizontal", length=200, mode="determinate")
ssd_progress_bar.pack()

# Create progress bars for CPU, RAM, and GPU usage
cpu_bar = Progressbar(root, orient="horizontal", length=200, mode="determinate")
cpu_bar.pack()

ram_bar = Progressbar(root, orient="horizontal", length=200, mode="determinate")
ram_bar.pack()

gpu_bar = Progressbar(root, orient="horizontal", length=200, mode="determinate")
gpu_bar.pack()

info_label = tk.Label(root, text="", font=("Helvetica", 12), justify='left')
info_label.pack()

keyboard_slider = tk.Scale(root, from_=0, to=1, orient="horizontal", label="Block Keyboard")
keyboard_slider.pack()

toggle_button = tk.Button(root, text="Toggle Keyboard Blocking", command=toggle_keyboard_block)
toggle_button.pack()

root.bind_all('<Key>', block_keyboard)

info_update_thread = threading.Thread(target=update_info_label)
info_update_thread.daemon = True
info_update_thread.start()

image = PhotoImage(file="SysOptiMaster-logo.png")
root.tk.call('wm', 'iconphoto', root._w, image)

system_tray_thread = threading.Thread(target=create_system_tray)
system_tray_thread.daemon = True
system_tray_thread.start()

# Start the SSD progress bar update thread
ssd_thread = threading.Thread(target=update_ssd_progress_bar)
ssd_thread.daemon = True
ssd_thread.start()

# Start the progress bars update thread
progress_bars_thread = threading.Thread(target=update_progress_bars)
progress_bars_thread.daemon = True
progress_bars_thread.start()

root.mainloop()     











