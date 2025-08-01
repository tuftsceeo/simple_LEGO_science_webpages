from pyscript import window, when, document
import asyncio 
import struct
from hubs import hubs
import channel
import math

sensor = hubs(1, verbose=False)
motor = hubs(2, verbose = False)

training_data = []
k = 3

motor_connected = False
sensor_connected = False

run_clickable = False
keep_running = True

stop_entry_index = 0
go_entry_index = 0
current_class="none"

training = False

def colorSensorConnect(event=None):
    global sensor_connected
    global motor_connected
    global current_class
    global training
    document.getElementById("motor-button-container").classList.add("unclickable")
    if sensor_connected:
        toggleSensorImage()
        sensor.hub.disconnect()
        window.console.log('sensor disconnected')
        sensor.list_update = False
        sensor.dropdown_menu.options.length = 0
        sensor_connected = False
    else:
        sensor.list_update = False
        await sensor.hub.connect()
        toggleSensorImage()
        window.console.log('sensor connected')
        sensor_connected = True
        await sensor.start_data_feed(event=None)
    
    if sensor_connected and motor_connected:
        show_next_class()
        training = True
    else:
        training = False
        document.getElementById("classes").style.display="none"
        document.getElementById("run-panel").style.display="none"
        current_class = "none"
    document.getElementById("motor-button-container").classList.remove("unclickable")

def singleMotorConnect(event=None):
    global motor_connected
    global sensor_connected
    global current_class
    global training
    document.getElementById("sensor-button-container").classList.add("unclickable")
    if motor_connected:
        toggleMotorImage()
        motor.hub.disconnect()
        window.console.log('motor disconnected')
        motor.list_update = False
        motor.dropdown_menu.options.length = 0
        motor_connected = False
    else:
        motor.list_update = False
        await motor.hub.connect()
        toggleMotorImage()
        window.console.log('motor connected')
        motor_connected = True

    if sensor_connected and motor_connected:
        show_next_class()
        training = True 
    else:
        training = False
        document.getElementById("classes").style.display="none"
        document.getElementById("run-panel").style.display="none"
        current_class = "none"
    document.getElementById("sensor-button-container").classList.remove("unclickable")
    
def toggleMotorImage():
    disconnected_img = "https://raw.githubusercontent.com/akaufman510/motorcontrolimages/main/motor-disconnected.png"
    connected_img = "https://raw.githubusercontent.com/akaufman510/motorcontrolimages/main/motor-connected-transparent.png"
    button = document.getElementById("motor-image")
    current_src = button.src
    button.src = connected_img if disconnected_img in current_src else disconnected_img

def toggleSensorImage():
    disconnected_img = "https://raw.githubusercontent.com/akaufman510/motorcontrolimages/main/color-sensor-disconnected.png"
    connected_img = "https://raw.githubusercontent.com/akaufman510/motorcontrolimages/main/color-sensor-connected.png"
    button = document.getElementById("sensor-image")
    current_src = button.src
    button.src = connected_img if disconnected_img in current_src else disconnected_img

def show_next_class():
    global current_class
    global run_clickable
    if current_class == "none":
        document.getElementById("classes").style.display = "block"
        toggle_gray_stop()
        current_class = "go"
        document.getElementById("go-entry-0").classList.toggle("preview-entry")
    elif current_class == "go":
        toggle_gray_go()
        toggle_gray_stop()
        current_class = "stop"
        document.getElementById("stop-entry-0").classList.toggle("preview-entry")
    elif current_class == "stop":
        toggle_gray_stop()
        document.getElementById("run-panel").style.display = "flex"
        current_class = "complete"
        run_clickable = True

def toggle_gray_go():
    document.getElementById("go-row").classList.toggle("gray-row")
    document.getElementById("keep-running-button").classList.toggle("gray-button")
    document.getElementById("keep-running-button").classList.toggle("unclickable")
    document.getElementById("go-class-box").classList.toggle("gray-class")

def toggle_gray_stop():
    document.getElementById("stop-row").classList.toggle("gray-row")
    document.getElementById("stop-running-button").classList.toggle("gray-button")
    document.getElementById("stop-running-button").classList.toggle("unclickable")
    document.getElementById("stop-class-box").classList.toggle("gray-class")
        
def train_go_button(event=None):
    global go_entry_index
    add_entry()
    go_entry_index += 1
    style_boxes()
    if go_entry_index >= 5:
        show_next_class()

def train_stop_button(event=None):
    global stop_entry_index
    global training
    add_entry()
    stop_entry_index += 1
    style_boxes()
    if stop_entry_index >= 5:
        show_next_class()
        training = False

def style_boxes():
    global go_entry_index
    global stop_entry_index
    global current_class
    if current_class == "go":
        current_box = document.getElementById(f"go-entry-{go_entry_index-1}")
        next_box = document.getElementById(f"go-entry-{go_entry_index}")
    elif current_class == "stop":
        current_box = document.getElementById(f"stop-entry-{stop_entry_index-1}")
        next_box = document.getElementById(f"stop-entry-{stop_entry_index}")
    else:
        print("class was neither go nor stop")
    current_box.classList.toggle("preview-entry")
    current_box.classList.toggle("filled-entry")
    color = get_color()
    current_box.style.backgroundColor = f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}"
    if next_box:
        next_box.classList.toggle("preview-entry")  

def highlight_go_class():
    document.getElementById("go-row").classList.remove("gray-row")
    document.getElementById("go-class-box").classList.remove("gray-class")
    document.getElementById("keep-running-button").classList.remove("gray-button")
    
    document.getElementById("stop-row").classList.add("gray-row")
    document.getElementById("stop-class-box").classList.add("gray-class")
    document.getElementById("stop-running-button").classList.add("gray-button")

def highlight_stop_class():
    document.getElementById("stop-row").classList.remove("gray-row")
    document.getElementById("stop-class-box").classList.remove("gray-class")
    document.getElementById("stop-running-button").classList.remove("gray-button")
    
    document.getElementById("go-row").classList.add("gray-row")
    document.getElementById("go-class-box").classList.add("gray-class")
    document.getElementById("keep-running-button").classList.add("gray-button")

def add_entry():
    global current_class
    global training_data
    color = get_color()
    training_data.append([color, current_class])

async def update_color():
    global training
    global go_entry_index
    global stop_entry_index
    global current_class
    while True:
        while training:
            # Check if training needs to be refreshed
            if (current_class == "go" and go_entry_index > 4) or (current_class == "stop" and stop_entry_index > 4):
                pass
            else:
                if current_class == "go":
                    current_box = document.getElementById(f"go-entry-{go_entry_index}")
                elif current_class == "stop":
                    current_box = document.getElementById(f"stop-entry-{stop_entry_index}")

                color = get_color()
                
                if color != None:
                    current_box.style.backgroundColor = f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}"
                    
            await asyncio.sleep(0.05)
            
        await asyncio.sleep(0.1)

def get_color():
    # math from chat
    data = sensor.reply
    if not data:
        print('no reply')
        return
    if 'Firmware' in data: 
        print('Firmware read')
        return
    if sensor.hub.info['device'] != 514:
        print('wrong device ')
        return
    h = int(data['hue'])
    s = int(data['saturation'])
    l = int(data['reflection'])
    # Convert H, S, L from 0–360 / 0–100 to 0.0–1.0
    h /= 360
    s /= 100
    l /= 100

    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h * 6) % 2 - 1))
    m = l - c / 2

    if 0 <= h < 1/6:
        r1, g1, b1 = c, x, 0
    elif 1/6 <= h < 2/6:
        r1, g1, b1 = x, c, 0
    elif 2/6 <= h < 3/6:
        r1, g1, b1 = 0, c, x
    elif 3/6 <= h < 4/6:
        r1, g1, b1 = 0, x, c
    elif 4/6 <= h < 5/6:
        r1, g1, b1 = x, 0, c
    else:
        r1, g1, b1 = c, 0, x

    r = int((r1 + m) * 255)
    g = int((g1 + m) * 255)
    b = int((b1 + m) * 255)
    return [r, g, b]

def get_nn_go_vote(point, k):
    global training_data
    distances = []
    go_votes = 0
    stop_votes = 0
    for entry in training_data:
        distances.append([get_distance(entry[0], point), entry[1]])
    distances.sort()
    for i in range(k):
        if distances[i][1] == "stop":
            stop_votes += 1
        else:
            go_votes += 1
    return go_votes > stop_votes

def get_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 + (point1[2] - point2[2])**2)

async def forwards(motor):
    await motor.motor_speed(3,50)
    await motor.motor_run(1,0)
    await motor.motor_run(2,1)

async def stop(motor):
    await motor.motor_speed(3,0)
    await motor.motor_run(3,0)

async def run(motor):
    global keep_running
    global k
    
    while keep_running:      
        if get_nn_go_vote(get_color(), k):
            highlight_go_class()
            await forwards(motor)
        else: 
            highlight_stop_class()
            await stop(motor)
        await asyncio.sleep(0.05)
    await stop(motor)

def stop_button(event=None):
    global keep_running
    keep_running = False

async def run_button(event=None):
    global run_clickable
    global motor
    global keep_running
    if run_clickable:
        changeButtons()
        await run(motor)
        changeButtons()
        keep_running = True

def changeButtons():
    global run_clickable
    if run_clickable:
        document.getElementById("run-button").style.backgroundColor="#c0e6bc"
        document.getElementById("stop-button").style.backgroundColor = "#f70505"
    else:
        document.getElementById("run-button").style.backgroundColor="#17e004"
        document.getElementById("stop-button").style.backgroundColor = "#fcacac"
    run_clickable = not run_clickable

asyncio.create_task(update_color())

(document.getElementById("motor-button-container")).onclick = singleMotorConnect
(document.getElementById("sensor-button-container")).onclick = colorSensorConnect
(document.getElementById("keep-running-button")).onclick = train_go_button
(document.getElementById("stop-running-button")).onclick = train_stop_button
(document.getElementById("run-button")).onclick = run_button
(document.getElementById("stop-button")).onclick = stop_button