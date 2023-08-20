#################CITATION 
import pyaudio
import crepe
import os
import numpy as np
import time
import matplotlib.pyplot as plt




def save_frequency_data(time_frame, frequency_frame,y_frame): ## array, array
    figure, axis = plt.subplots(2)

    # frequency_plot
    axis[0].plot(time_frame, frequency_frame)
    axis[0].set_title("frequency_plot.png")
    
    # wav_amplitude
    axis[1].plot(time_frame, y_frame)
    axis[1].set_title("wav_amplitude_plot.png")
    

    plt.savefig("plots.png")
    plt.show()
        
    




os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Hide TF logging

CHUNK = 1024  # Number of samples per buffer
WIDTH = 2  # Bytes per sample
CHANNELS = 1  # Mono sound
RATE = 16000  # Sampling rate (number of samples per second)

time_list = []
frequency_list = []
y_list = []

try:
    at = []
    cur_time = 0

    print("Recording is starting...")
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(WIDTH),
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    while True:
        st = time.time()

        bytes_data = stream.read(CHUNK)
        nparray_data = np.frombuffer(bytes_data, dtype=np.int16)  # Convert bytes to NumPy ndarray
        print(nparray_data)
        
        time_f, frequency, confidence, activation = crepe.predict(nparray_data, RATE, model_capacity="tiny",
                                                                  step_size=65, verbose=0)

        # Console outcome
        confidence_flag = True
        confidence_mark = "🟩"
        if confidence[0] <= 0.7:
            confidence_mark = "🟥"
            confidence_flag = False
        #     print(f"{confidence_mark} {round(frequency[0], 1)} Hz | {confidence[0]}")
        # else:
        print(f"{confidence_mark} {round(frequency[0], 1)} Hz | {confidence[0]} ")

        at.append(time.time() - st)
        cur_time += time.time() - st
        time_list.append(cur_time)
        if confidence_flag == True:
            frequency_list.append(round(frequency[0], 1))
        else:
            frequency_list.append(round(0, 1))
            
except KeyboardInterrupt:
    
    save_frequency_data(time_list, frequency_list,y_list)
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Recording stopped")

    at.pop(0)
    print(f"Average time per frame: {round(sum(at) / len(at), 3)} sec.")
