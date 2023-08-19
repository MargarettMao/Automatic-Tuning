import sounddevice
import pyaudio
import crepe
import numpy as np
import os
import random
import time
import signal
import sys
from datetime import datetime
import matplotlib.pyplot as plt
from configuration import *

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Hide TF logging

# I can do resampling if the velocity is not good. 
# I am able to do the pitch controller. 

# turing lest: the pitch will increase
# turning right: the pitch will descrease 
# PD Controller setting
Kp = 1
Kd = 0.5

# File writing
f = open("angle_information_pitch_involved.txt", "a")
f = open("angle_information_pitch_involved.txt", "w")

# Launch Motor 
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Stop the Torque with ctrl c signal
def exit_handler(signal, frame):
    print("\nExiting...")
    # Disable Dynamixel Torquecurrent_position
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    portHandler.closePort()
    sys.exit(0)

def pitch_recognition():
    # record for several second:
    # as long as the HIGH CONFIDENCE STANDS FOR FIVE SECONDES: then I will take the AVERAGE of the pitch as my goal
    # PITCH as feed after

    # continuously stream untill the high conficence appear for more than 5 secs. 
    # take average.
    # store the frequency. 
    at = []
    pitch_frec_total = 0
    count = 0
    print("==Start recognizing==")
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(WIDTH),
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    # Prepare Plotting
    plot_data = np.random.rand(360, 50)
    fig = plt.figure()
    ax = fig.add_subplot()
    line = ax.imshow(plot_data, cmap='inferno', origin='lower', extent=[0, 100, 0, 50])

    while True:
        st = time.time()
        # Get mic data
        bytes_data = stream.read(CHUNK)
        nparray_data = np.frombuffer(bytes_data, dtype=np.int16)  # Convert bytes to NumPy ndarray

        # Predict pitches
        frame, frequency, confidence, activation = crepe.predict(nparray_data, RATE, model_capacity="tiny",
                                                                 step_size=65, verbose=0)

        # Convert data
        activation = np.reshape(activation, (360, 1))
        plot_data = np.append(plot_data, activation, axis=1)
        plot_data = np.delete(plot_data, 0, axis=1)

        if confidence[0] > 0.7:
            pitch_frec_total += frequency[0]
            count += 1
            plt.title(f"Voice pitch: {round(frequency[0], 1)} Hz\n"
                      f"Confidence: {'{:.2f}'.format(confidence[0])}")  # round() doesn't work properly
            if count >= 5:
                print("I've plucked the string")
                stream.stop_stream()
                stream.close()
                p.terminate()
                plt.close('all')

                at.pop(0)
                print(f"Average time per frame: {round(sum(at) / len(at), 3)} sec.")
                print("========Finish Recognizing========")
                return pitch_frec_total/5 # This is the average pitch
        else:
            pitch_frec_total = 0 
            count = 0
            plt.title("Voice pitch:\n"
                      f"Confidence: {'{:.2f}'.format(confidence[0])}")
        # Plotting
        line.set_data(plot_data)
        plt.pause(0.001)
        ax.relim()  # recompute the ax.dataLim
        ax.autoscale_view()  # update ax.viewLim using the new dataLim

        at.append(time.time() - st)
    


def launch_robot(goal_pitch): # add target pitch 
    success_count = 0
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
    # Change Operating mode 
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_OPERATING_MODE, VELOCITY_CONTROL_MODE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        # print("%s" % packetHandler.getRxPacketError(dxl_error-128))
        print("This is error one operating mode: ", dxl_error)
    if dxl_error == 128:
        print("OPERATING MODE CHANGED: VELOCITY_CONTROL_MODE")
    # Enable Dynamixel Torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
        # exit()
        if dxl_error != 128:
            exit()
    current_pitch = 0
    last_error = 0
    while True:
        random_velocity = random.randint(0,100)#(0, 1023)
        # Apply PD control to set goal current
        error = goal_pitch - current_pitch
        derivative = error - last_error
        coi = Kp * error + Kd*derivative
        coi /= goal_pitch
        last_error = error
        random_velocity *= coi * 10 
        print("This is the current velocity:", random_velocity)
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_VELOCITY, -int(random_velocity))
        # dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL_ID, ADDR_PRO_GOAL_CURRENT, torque)
        f.write(str(error))
        f.write("\t")
        f.write(str(current_pitch))
        f.write("\n")
        time.sleep(3)
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_VELOCITY, 0)
        print("==MOVE FROM ROBOT TO AUDIO==")
        current_pitch = pitch_recognition()
        #### read current pitch frequency and compare with previous ones 
        print("==BACK TO ROBOT==")
        dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, DXL_ID, ADDR_READ_PRESENT_POS)
        if dxl_comm_result == COMM_SUCCESS:
            current_position = dxl_present_position
            print(f"This is the goal pitch {goal_pitch}, This is position error {error}, this is current pitch: {current_pitch}")
        print (f"======IMPORTANT: THIS IS THE CURRENT PITCH {'{:.2f}'.format(current_pitch)}=====")
        if not abs( current_pitch - goal_pitch) > PITCH_THRESHOLD:
            success_count += 1
            if success_count >= 4:
                print("SUCCEED")
                break

def main():
    # Set the stop signal 
    signal.signal(signal.SIGINT, exit_handler)
    
    goal_pitch = 392

    launch_robot(goal_pitch)
    # current_position = 0
    # last_error = 0

    



        
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