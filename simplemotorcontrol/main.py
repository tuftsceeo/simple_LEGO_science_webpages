from pyscript import document, window, when
import asyncio 
from js import performance
from hubs import hubs

x = hubs(1)

direction = -1
run_clickable = True
should_run = True
connection = False

def clockwiseButton(event=None):
    global direction
    direction = 1
    button = document.getElementById("clockwise-button")
    other_button = document.getElementById("counterclockwise-button")
    other_button.style.borderColor="transparent"
    button.style.borderColor="#555"

def counterclockwiseButton(event=None):
    global direction
    direction = -1
    button = document.getElementById("counterclockwise-button")
    other_button = document.getElementById("clockwise-button")
    other_button.style.borderColor="transparent"
    button.style.borderColor="#555"

def increaseTime(event=None):
    time_box = document.getElementById("time-input")
    time = int(time_box.value)
    if time >=90:
        pass
    else:
        time_box.value = int(time_box.value) + 1

def decreaseTime(event=None):
    time_box = document.getElementById("time-input")
    time = int(time_box.value)
    if time <=0:
        pass
    else:
        time_box.value = int(time_box.value) - 1

async def runButton(event=None):
    if run_clickable:
        changeButtons()
        await runActions()
        changeButtons()
        should_run = True
    
async def runActions():
    global direction
    global should_run
    should_run = True
    await x.motor_speed(1, 50*direction)
    await x.motor_run(1,0)
    desired_time = float(document.getElementById("time-input").value)
    
    start = performance.now()
    while (performance.now() - start) < 1000*desired_time:
        if not should_run:
            await x.motor_speed(1,0)
            await x.motor_run(1,0)
            should_run = True
            return
        await asyncio.sleep(0.05)
    await x.motor_speed(1,0)
    await x.motor_run(1,0)
    

def stopButton(event=None):
    global should_run
    should_run = False

def changeButtons():
    global run_clickable
    if run_clickable:
        document.getElementById("run-button").style.backgroundColor="#c0e6bc"
        document.getElementById("stop-button").style.backgroundColor = "#f70505"
    else:
        document.getElementById("run-button").style.backgroundColor="#17e004"
        document.getElementById("stop-button").style.backgroundColor = "#fcacac"
    run_clickable = not run_clickable

def singleMotorConnect(event=None):
    global connection
    if connection:
        toggleMotorImage()
        x.hub.disconnect()
        window.console.log('disconnected')
        x.list_update = False
        x.dropdown_menu.options.length = 0
        document.getElementById("motor-control-popup").style.display="none"
        connection = False
    else:
        x.list_update = False
        await x.hub.connect()
        toggleMotorImage()
        window.console.log('connected')
        document.getElementById("motor-control-popup").style.display="flex"
        connection = True

def toggleMotorImage():
    global connection
    disconnected_img = "https://raw.githubusercontent.com/akaufman510/motorcontrolimages/main/motor-disconnected.png"
    connected_img = "https://raw.githubusercontent.com/akaufman510/motorcontrolimages/main/motor-connected-transparent.png"
    button = document.getElementById("motor-button")
    current_src = button.src
    button.src = connected_img if disconnected_img in current_src else disconnected_img
    connection = not connection

(document.getElementById("counterclockwise-button")).style.borderColor="#555"
(document.getElementById("clockwise-button")).onclick = clockwiseButton
(document.getElementById("counterclockwise-button")).onclick = counterclockwiseButton
(document.getElementById("time-increase")).onclick = increaseTime
(document.getElementById("time-decrease")).onclick = decreaseTime
(document.getElementById("run-button")).onclick = runButton
(document.getElementById("stop-button")).onclick = stopButton
(document.getElementById("motor-button-container")).onclick = singleMotorConnect
