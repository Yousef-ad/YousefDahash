import tkinter as tk
from tkinter import IntVar
from tkinter import ttk
import time
from Congestion_Estimation import *
from Video_Processing import *
from Ramp_Regulater import *
from Network_Handler import *

video_path = "Green3.mp4"
average_speed = 0
congestion_level = 'null'
TOR = 0

pause = True  
button_text = "Pause"

#connect to USB port
usb_port = get_arduino_port()


def update_gui(average_speed, congestion_level, TOR):
    # Update GUI
    speed_label_value.config(text="{} km/h".format(int(average_speed)))
    congestion_label_value.config(text="{}".format(congestion_level))
    tor_label_value.config(text="{}s".format(TOR))
    
    color_map = {"1": "dark red", "2": "red", "3": "yellow", "4": "green"}
    color = color_map.get(congestion_level, "grey")  
    color_box.config(background=color)
    root.update()

def pause_action():
    global pause, button_text
    pause = True            
    button_text = "Pause"  
    
def start_action():
    global pause, button_text
    pause = False
    button_text = "Start"
    
# Create GUI window
root = tk.Tk()
root.title("Traffic Information")
root.geometry("340x270")  
root.configure(bg="#f0f0f0") 

# Create a style
style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 14))
style.configure("TButton", font=("Helvetica", 14), padding=10)

main_frame = ttk.Frame(root)
main_frame.grid(row=0, column=0, padx=20, pady=20)

# Create labels for displaying information
speed_label = ttk.Label(main_frame, text="Average Speed:")
speed_label.grid(row=0, column=0, sticky='w', pady=5)

speed_label_value = ttk.Label(main_frame, text="0 km/h", relief="solid", padding="5 5 5 5", background="#F4F8FB")
speed_label_value.grid(row=0, column=1, sticky='w', pady=5)


congestion_label = ttk.Label(main_frame, text="Congestion Level:")
congestion_label.grid(row=1, column=0, sticky='w', pady=5)

congestion_label_value = ttk.Label(main_frame, text="null", relief="solid", padding="5 5 5 5", background="#F4F8FB")
congestion_label_value.grid(row=1, column=1, sticky='w', pady=5)


tor_label = ttk.Label(main_frame, text="TOR:")
tor_label.grid(row=2, column=0, sticky='w', pady=5)

tor_label_value = ttk.Label(main_frame, text="0s", relief="solid", padding="5 5 5 5", background="#F4F8FB")
tor_label_value.grid(row=2, column=1, sticky='w', pady=5)


# Create color box
color_box = tk.Label(main_frame, width=10, height=1, relief="solid", bd=1, background="grey")
color_box.grid(row=3, column=0, pady=10, sticky='w')

# Create buttons
pause_button = ttk.Button(main_frame, text="Pause", command=pause_action)
pause_button.grid(row=4, column=0, pady=10)

start_button = ttk.Button(main_frame, text="Start", command=start_action)
start_button.grid(row=4, column=1, pady=10)

while True:
    update_gui(average_speed, congestion_level, TOR)
    if pause:
        root.update()
        continue  

    speed_data = video_processing(video_path)  # 30 seconds execution
    congestion_level, average_speed = congestion_estimation(speed_data)
    if congestion_level!= "-1":
        TOR = Ramp_Regulater(congestion_level)
        #send_TOR('SET TOR', TOR, usb_port)

    # time.sleep(5)

root.mainloop()
