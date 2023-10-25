import psutil
import GPUtil
import time
import tkinter as tk
import threading
import pystray
from PIL import Image
from tkinter import PhotoImage

keyboard_blocked = False

def get_cpu_ram_usage():
    cpu_usage = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    ram_usage = ram.percent

    cpu_temperature = get_cpu_temperature()
    gpu_usage = get_gpu_usage()

    return f"CPU: {cpu_usage:.1f}% | RAM: {ram_usage:.1f}% | {gpu_usage}"

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

def update_info_label():
    while True:
        usage_text = get_cpu_ram_usage()
        info_label.config(text=f"{usage_text}\n{get_cpu_temperature()}")
        time.sleep(1)

def toggle_visibility(event):
    if root.winfo_viewable():
        root.iconify()
    else:
        root.deiconify()

def create_system_tray():
    menu = pystray.Menu(pystray.MenuItem('Open', toggle_visibility))
    image = Image.open('SysOptiMaster.png')
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

root = tk.Tk()
root.title("SysOptiMaster")
root.attributes('-alpha', 0.7)

cpu_gpu_ram_label = tk.Label(root, text="", font=("Helvetica", 12), justify='left')
cpu_gpu_ram_label.pack()

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

image = PhotoImage(file="SysOptiMaster.png")
root.tk.call('wm', 'iconphoto', root._w, image)

system_tray_thread = threading.Thread(target=create_system_tray)
system_tray_thread.daemon = True
system_tray_thread.start()

root.mainloop()










