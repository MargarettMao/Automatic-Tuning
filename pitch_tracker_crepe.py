import crepe
from scipy.io import wavfile
import matplotlib.pyplot as plt
# f = open("standard_pitch_four.txt", "w")
# f = open("standard_pitch_four.txt", "a")
sr, audio = wavfile.read('tuning_5.wav')
print(sr,audio)
print(type(sr),type(audio))
print(len(audio))
plt.plot(audio)
plt.show()
# time, frequency, confidence, activation = crepe.predict(audio, sr, viterbi=True)
# print(time, frequency, confidence, activation )
# x = time 
# y = frequency
# plt.plot(x,y)
# plt.xlabel('time')
# plt.ylabel('frequency')
# plt.savefig('standard_pitch_four.png')
# for i in range(len(time)):
# 	f.write("time: ")
# 	f.write(str(time[i]))
# 	f.write("	")
# 	f.write("frequency: ")
# 	f.write(str(frequency[i]))
# 	f.write("\n")

# for i in range(len(frequency)):
# 	print(frequency[i])
# 	print(time[i])