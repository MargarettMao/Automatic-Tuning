######
# I assume that the default operating mode is the position mode

# one application: setting up the getch
import os
import time

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

from dynamixel_sdk import * # Uses Dynamixel SDK library
from configuration import * 

GOAL_POSITION               = 200   # The maximum velocity it can choose is 330
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
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_OPERATING_MODE, EXTENED_POSITION_MODE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    # print("%s" % packetHandler.getRxPacketError(dxl_error-128))
    print("This is error one operating mode: ", dxl_error)
if dxl_error == 128:
    print("OPERATING MODE CHANGED: EXTENED_POSITION_MODE")

# Enable the torque
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
    print("This is error two torque: ", dxl_error)
if dxl_error == 128:
    print("TORQUE ENABLE")

# # Check harware error
# # The error output is 1: Bit 0: Input Voltage Error is 1: Detects that input voltage exceeds the configured operating voltage
# dxl_hardware_error, dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, DXL_ID, ADDR_HARDWARE_ERROR)
# if dxl_comm_result != COMM_SUCCESS:
#     print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
# elif dxl_error != 0:
#     print("%s" % packetHandler.getRxPacketError(dxl_error))
#     print("This is error zero error_read: ", dxl_error)
# print("This is the value for the error output: ", dxl_hardware_error)

# ### Set the velocity gradully (But how gradually) 
### Set the velocity and wait 10 seconds at the time you hit the velocity

# Set goal position
dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_POSITION,GOAL_POSITION)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    # print("%s" % packetHandler.getRxPacketError(dxl_error-128))
    print("This is error three setgoal: ", dxl_error)
if dxl_error == 128:
    print("SET GOAL POSITION SUCCESSFULLY")

# Read present velocity
while 1:
    PRESENT_POSITION, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, DXL_ID, ADDR_READ_PRESENT_POS)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        # print("%s" % packetHandler.getRxPacketError(dxl_error-128))
        print("This is error four read_position: ", dxl_error)
    if dxl_error == 128:
        print("READ PRESENT VELOCITY SUCCESSFULLY")
    print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL_ID, GOAL_POSITION, PRESENT_POSITION))
    if not abs(GOAL_POSITION - PRESENT_POSITION) > DXL_MOVING_STATUS_THRESHOLD:
        break

# # # Try to set velocity to zero again:
# # dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_VELOCITY, 0)
# # if dxl_comm_result != COMM_SUCCESS:
# #     print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
# # elif dxl_error != 0:
# #     # print("%s" % packetHandler.getRxPacketError(dxl_error-128))
# #     print("This is error five set_vel_zero: ", dxl_error)
# # if dxl_error ==128:
# #     print("SET VEL TO ZERO SUCCESSFULLY")

# # # Read present velocity
# # while 1:
# #     PRESENT_VELOCITY, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, DXL_ID, ADDR_READ_PRESENT_VELOCITY)
# #     if dxl_comm_result != COMM_SUCCESS:
# #         print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
# #     elif dxl_error != 0:
# #         # print("%s" % packetHandler.getRxPacketError(dxl_error-128))
# #         print("This is error four read_position: ", dxl_error)
# #     if dxl_error == 128:
# #         print("READ PRESENT VELOCITY SUCCESSFULLY")
# #     print("[ID:%03d] GoalVel:%03d  PresVel:%03d" % (DXL_ID, GOAL_VELOCITY, PRESENT_VELOCITY))
# #     if not abs(GOAL_VELOCITY - PRESENT_VELOCITY) > DXL_MOVING_STATUS_THRESHOLD:
# #         break


# # # Read present position constantly
# # while 1:
# #     dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, DXL_ID, ADDR_READ_PRESENT_POSITION)
# #     if dxl_comm_result != COMM_SUCCESS:
# #         print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
# #     elif dxl_error != 0:
# #         print("%s" % packetHandler.getRxPacketError(dxl_error))
# #         print("This is error three read_position: ", dxl_error)

# #     print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL_ID, dxl_goal_position[position_index], dxl_present_position))
# #     if not abs(dxl_goal_position[position_index] - dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD:
# #         break

# Disable the torque
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
    print("This is error six torque_dis: ", dxl_error)
if dxl_error == 128:
    print("TORQUE DISABLE")

# Close port
portHandler.closePort()
