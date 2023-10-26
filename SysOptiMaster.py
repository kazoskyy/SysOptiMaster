import psutil
import subprocess
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
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        ram_usage = ram.percent
        gpu_usage = get_gpu_usage()
        return cpu_usage, ram_usage, gpu_usage
    except Exception as e:
        return None, None, str(e)

def get_gpu_usage():
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'], stdout=subprocess.PIPE, text=True)
        gpu_usage = float(result.stdout.strip())
        return f"GPU: {gpu_usage:.1f}%"
    except Exception as e:
        return "No GPU"

def get_ssd_usage():
    ssd = psutil.disk_usage('/')
    return ssd.percent

def update_ssd_progress_bar():
    while True:
        ssd_usage = get_ssd_usage()
        ssd_progress_bar['value'] = ssd_usage
        ssd_label.config(text=f"SSD Usage: {ssd_usage:.1f}%")
        root.update()
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

    root.iconbitmap(default='SysOptiMaster-logo.png')

def toggle_keyboard_block():
    global keyboard_blocked
    keyboard_blocked = not keyboard_blocked

def block_keyboard(event):
    print(f"keyboard_blocked: {keyboard_blocked}")  # Debug print
    if keyboard_blocked:
        return 'break'
    else:
        return None

def update_progress_bars():
    while True:
        cpu_usage, ram_usage, gpu_usage = get_cpu_ram_usage()
        gpu_usage_float = float(gpu_usage.split(' ')[-1][:-1]) if "GPU:" in gpu_usage else 0.0
        cpu_bar['value'] = cpu_usage
        ram_bar['value'] = ram_usage
        gpu_bar['value'] = gpu_usage_float
        # Display usage percentage next to the bars
        cpu_label.config(text=f"CPU: {cpu_usage:.1f}%")
        ram_label.config(text=f"RAM: {ram_usage:.1f}%")
        gpu_label.config(text=f"GPU: {gpu_usage_float:.1f}%")
        time.sleep(1)

root = tk.Tk()
root.title("SysOptiMaster")
root.attributes('-alpha', 0.9)  # Corrected

# Set minimum and maximum size to prevent resizing
root.minsize(400, 200)
root.maxsize(400, 200)

info_frame = tk.Frame(root)
info_frame.pack()

cpu_label = tk.Label(info_frame, text="CPU: 0%", font=("Helvetica", 12), justify='left')
cpu_label.grid(row=0, column=0, padx=10, sticky='w')

gpu_label = tk.Label(info_frame, text="GPU: 0%", font=("Helvetica", 12), justify='left')
gpu_label.grid(row=1, column=0, padx=10, sticky='w')

ram_label = tk.Label(info_frame, text="RAM: 0%", font=("Helvetica", 12), justify='left')
ram_label.grid(row=2, column=0, padx=10, sticky='w')

ssd_label = tk.Label(info_frame, text="SSD: 0%", font=("Helvetica", 12), justify='left')
ssd_label.grid(row=3, column=0, padx=10, sticky='w')

info_label = tk.Label(info_frame, text="", font=("Helvetica", 12), justify='left')
info_label.grid(row=4, column=0, padx=10, sticky='w')

ssd_progress_bar = Progressbar(info_frame, orient="horizontal", length=200, mode="determinate")
ssd_progress_bar.grid(row=3, column=1, padx=10)

cpu_bar = Progressbar(info_frame, orient="horizontal", length=200, mode="determinate")
cpu_bar.grid(row=0, column=1, padx=10)

ram_bar = Progressbar(info_frame, orient="horizontal", length=200, mode="determinate")
ram_bar.grid(row=2, column=1, padx=10)

gpu_bar = Progressbar(info_frame, orient="horizontal", length=200, mode="determinate")
gpu_bar.grid(row=1, column=1, padx=10)

keyboard_slider = tk.Scale(root, from_=0, to=1, orient="horizontal", label="Block Keyboard")
keyboard_slider.pack()

toggle_button = tk.Button(root, text="Toggle Keyboard Blocking", command=toggle_keyboard_block)
toggle_button.pack()
root.bind_all('<Key>', block_keyboard)

image = PhotoImage(file="SysOptiMaster-logo.png")
root.tk.call('wm', 'iconphoto', root._w, image)

system_tray_thread = threading.Thread(target=create_system_tray)
system_tray_thread.daemon = True
system_tray_thread.start()

ssd_thread = threading.Thread(target=update_ssd_progress_bar)
ssd_thread.daemon = True
ssd_thread.start()

progress_bars_thread = threading.Thread(target=update_progress_bars)
progress_bars_thread.daemon = True
progress_bars_thread.start()

root.mainloop()

