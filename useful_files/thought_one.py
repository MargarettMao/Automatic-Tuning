######
# I assume that the default operating mode is the position mode

# one application: setting up the getch
import os
import time
import pyaudio
import crepe
import numpy as np
import matplotlib.pyplot as plt
from dynamixel_sdk import * # Uses Dynamixel SDK library

# Robot Setting Up
if os.name == 'nt':

    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
MY_DXL                      = 'X_SERIES'   
ADDR_TORQUE_ENABLE          = 64#562       # Control table address is different in DYNAMIXEL model
ADDR_GOAL_VELOCITY          = 104
ADDR_READ_PRESENT_VELOCITY  = 128#611
ADDR_HARDWARE_ERROR         = 70
ADDR_OPERATING_MODE         = 11

COMM_SUCCESS                = 0

VELOCITY_CONTROL_MODE       = 1
GOAL_VELOCITY               = 100   # The maximum velocity it can choose is 330
# velocity value limit: 1 -- 1023
BAUDRATE                    = 57600
PROTOCOL_VERSION            = 2.0
DXL_ID                      = 1
DEVICENAME                  = '/dev/ttyUSB0'
TORQUE_ENABLE               = 1     # Value for enabling the torque
TORQUE_DISABLE              = 0     # Value for disabling the torque
DXL_MOVING_STATUS_THRESHOLD = 5    # the final difference you want # Dynamixel moving status threshold

# Initialize
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()

# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()

# Change Operating mode 
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_OPERATING_MODE, VELOCITY_CONTROL_MODE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    # print("%s" % packetHandler.getRxPacketError(dxl_error-128))
    print("This is error one operating mode: ", dxl_error)
if dxl_error == 128:
    print("OPERATING MODE CHANGED: VELOCITY CONTROL MODE")

# Enable the torque
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    # print("%s" % packetHandler.getRxPacketError(dxl_error))
    print("This is error two torque: ", dxl_error)
if dxl_error == 128:
    print("TORQUE ENABLE")

# Pitch Setting Up 
CHUNK = 1024  # Number of samples per buffer
WIDTH = 2  # Bytes per sample
CHANNELS = 1  # Mono sound
RATE = 16000  # Sampling rate (number of samples per second)

while True:
    print("START PITCH RECOGNITION")
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(WIDTH),channels=CHANNELS,rate=RATE,input=True,
                    frames_per_buffer=CHUNK)
    correct_count = 0
    while True:
        st = time.time()
        bytes_data = stream.read(CHUNK)
        nparray_data = np.frombuffer(bytes_data, dtype=np.int16)  # Convert bytes to NumPy ndarray
        frame, frequency, confidence, activation = crepe.predict(nparray_data, RATE, model_capacity="tiny",
                                                            step_size=65, verbose=0)
        correct_mark = "🟩"
        if confidence[0] > 0.7:
            if abs(frequency[0] - 350) <= 2:
                correct_count += 1 
                print(f"{correct_mark} {round(frequency[0], 1)} Hz | {confidence[0]}") 
                break       

    print("START ROTATE")
    # ### Set the velocity gradully (But how gradually) 
    ### Set the velocity and wait 10 seconds at the time you hit the velocity
    # Set goal velocity
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_VELOCITY,GOAL_VELOCITY)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        # print("%s" % packetHandler.getRxPacketError(dxl_error-128))
        print("This is error three setgoal: ", dxl_error)
    if dxl_error == 128:
        print("SET GOAL VELOCITY SUCCESSFULLY")

    # Read present velocity
    while 1:
        PRESENT_VELOCITY, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, DXL_ID, ADDR_READ_PRESENT_VELOCITY)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            # print("%s" % packetHandler.getRxPacketError(dxl_error-128))
            print("This is error four read_position: ", dxl_error)
        if dxl_error == 128:
            print("READ PRESENT VELOCITY SUCCESSFULLY")
        print("[ID:%03d] GoalVel:%03d  PresVel:%03d" % (DXL_ID, GOAL_VELOCITY, PRESENT_VELOCITY))
        if not abs(GOAL_VELOCITY - PRESENT_VELOCITY) > DXL_MOVING_STATUS_THRESHOLD:
            time.sleep(3)
            break
    # break


# # # Check harware error
# # # The error output is 1: Bit 0: Input Voltage Error is 1: Detects that input voltage exceeds the configured operating voltage
# # dxl_hardware_error, dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, DXL_ID, ADDR_HARDWARE_ERROR)
# # if dxl_comm_result != COMM_SUCCESS:
# #     print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
# # elif dxl_error != 0:
# #     print("%s" % packetHandler.getRxPacketError(dxl_error))
# #     print("This is error zero error_read: ", dxl_error)
# # print("This is the value for the error output: ", dxl_hardware_error)


# Disable the torque
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    # print("%s" % packetHandler.getRxPacketError(dxl_error))
    print("This is error six torque_dis: ", dxl_error)
if dxl_error == 128:
    print("TORQUE DISABLE")

# Close port
portHandler.closePort()
