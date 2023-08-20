import matplotlib.pyplot as plt


f = open("angle_information_pitch_involved.txt", "r")

x_time = []
y_position = []

content = f.readlines()
count = 1 
for line in content:
    error, current_position = (line).split("\t")
    if float(current_position) > 100000:
        continue
    x_time.append(count)
    y_position.append(float(current_position))
    count += 1 


print(len(x_time))
print(x_time)
print(y_position)
print(len(y_position))
# x = [1,2,3,4,5,6,7,8,9,10]
# y = [1,10000,400,5000,5,6933,14000,63,765,7333]
plt.plot(x_time,y_position)

# plt.axis([0, 20, 7000, 12000])
plt.show()