import matplotlib.pyplot as plt

def create_x_y(information_list):
    x_angle_list = []
    y_pitch_list = []
    pre_angle = 0
    for line in information_list:
        angle,start,end,_ = line.split('\t')
        angle = int(angle[5:])
        start = float(start)
        end = float(end)
        x_angle_list.append(pre_angle)
        y_pitch_list.append(start)
        pre_angle += angle
    x_angle_list.append(pre_angle)
    y_pitch_list.append(end)
    return x_angle_list,y_pitch_list

def main():
    f = open("angle_pitch.txt")

    content = f.readlines()
    content_sec1 = content[1:13]
    content_sec2 = content[15:27]
    print(content_sec1,len(content_sec1))
    print(content_sec2,len(content_sec2)) 
    one_x,one_y = create_x_y(content_sec1)
    two_x,two_y = create_x_y(content_sec2)
    print("-------=======-------")
    plt.xlabel("rotation angle")
    plt.ylabel("pitch in frequency representation")
    plt.plot(one_x,one_y,label="experiment one (12 rotations in total)",marker= '.')
    plt.plot(two_x,two_y, label = "experiment two (12 rotations in total)",marker= '.')
    plt.legend()
    plt.show()


if __name__ == '__main__':
  main()

