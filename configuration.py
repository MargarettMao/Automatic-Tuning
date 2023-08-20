from dynamixel_sdk import * # Uses Dynamixel SDK library

COMM_SUCCESS                = 0

# Motor CONFIGURATION
BAUDRATE                    = 57600
PROTOCOL_VERSION            = 2.0
DXL_ID                      = 1
DEVICENAME                  = '/dev/ttyUSB0'

# ADDR CONFIGURATION 
MY_DXL                      = 'X_SERIES'   
ADDR_TORQUE_ENABLE          = 64#562       # Control table address is different in DYNAMIXEL model
ADDR_GOAL_POSITION          = 116
ADDR_READ_PRESENT_POS       = 132
ADDR_GOAL_VELOCITY          = 104
ADDR_READ_PRESENT_VELOCITY  = 128#611
ADDR_HARDWARE_ERROR         = 70
ADDR_OPERATING_MODE         = 11
ADDR_GOAL_CURRENT           = 102
ADDR_READ_PRESENT_CURRENT   = 126

VELOCITY_CONTROL_MODE       = 1
POSITION_CONTROL_MODE       = 3
EXTENED_POSITION_MODE       = 4
CURRENT_BAS_POS_MODE        = 5
TORQUE_ENABLE               = 1     # Value for enabling the torque
TORQUE_DISABLE              = 0     # Value for disabling the torque

PITCH_THRESHOLD             = 1   # The maximum difference between goal and current 

# audio configuration
CHUNK = 1024  # Number of samples per buffer
WIDTH = 2  # Bytes per sample
CHANNELS = 1  # Mono sound
RATE = 16000  # Sampling rate (number of samples per second)