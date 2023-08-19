import os
import random
import time
import signal
import sys
from configuration import *
from datetime import datetime

# PD Controller setting
Kp = 1.5
Kd = 0.5

# File writing
f = open("angle_information.txt", "a")
f = open("angle_information.txt", "w")




# Launch Motor 
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Stop the Torque with ctrl c signal
def exit_handler(signal, frame):
    print("\nExiting...")
    # Disable Dynamixel Torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    portHandler.closePort()
    sys.exit(0)


def main():
    # Set the stop signal 
    signal.signal(signal.SIGINT, exit_handler)
    # Open port
    if portHandler.openPort():
        print("Port opened")
    else:
        print("Failed to open port")
        exit()
    # Set port baudrate
    if portHandler.setBaudRate(BAUDRATE):
        print("Baudrate set")
    else:
        print("Failed to change baudrate")
        exit()
    # Enable Dynamixel Torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
        # exit()
        if dxl_error != 128:
            exit()

    # Change Operating mode 
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_OPERATING_MODE, EXTENED_POSITION_MODE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        # print("%s" % packetHandler.getRxPacketError(dxl_error-128))
        print("This is error one operating mode: ", dxl_error)
    if dxl_error == 128:
        print("OPERATING MODE CHANGED: CURRENT_BAS_POS_MODE")

    goal_position = 20000
    current_position = 0
    last_error = 0
    while True:
        
        random_velocity = random.randint(0,110)#(0, 1023)

        # Apply PD control to set goal current
        error = goal_position - current_position
        derivative = error - last_error
        coi = Kp * error + Kd*derivative
        coi /= goal_position
        last_error = error
        random_velocity *= coi 

        print("This is the current velocity:", random_velocity)


        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_VELOCITY, int(random_velocity))
        # dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL_ID, ADDR_PRO_GOAL_CURRENT, torque)

        f.write(str(error))
        f.write("\t")
        f.write(str(current_position))
        f.write("\n")

        dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, DXL_ID, ADDR_READ_PRESENT_POS)
        if dxl_comm_result == COMM_SUCCESS:
            current_position = dxl_present_position
            print(f"This is the goal position {goal_position}, This is position error {error}, this is current position: {current_position}")
        time.sleep(1)



        
        # Generate random position and velocity
        
        
        # current_position = packetHandler.read4ByteTxRx(portHandler, DXL_ID, ADDR_READ_PRESENT_POS)[0]
        # cur_error = current_position- goal_position 
        # print(cur_error)
        # if cur_error > 0:
        #     random_velocity = -random_velocity
        # dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_POSITION, random_position)
        # dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_VELOCITY, random_velocity)
        # error = abs(random_position - packetHandler.read4ByteTxRx(portHandler, DXL_ID, ADDR_READ_PRESENT_POS)[0])
        # derivative = abs(random_velocity - packetHandler.read4ByteTxRx(portHandler, DXL_ID, ADDR_READ_PRESENT_VELOCITY)[0])
        # print(f"This is position error {error}, this is speed error {derivative}")
        # PD_output = Kp*error + Kd*derivative
        # print(f"New goal position: {random_position}, New goal velocity: {random_velocity}, PD output: {PD_output}")
        # time.sleep(1)
        


if __name__ == "__main__":
    main()