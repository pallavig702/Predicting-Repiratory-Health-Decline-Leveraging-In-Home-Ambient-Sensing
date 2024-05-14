import numpy as np
#from static.bed_data import r1, r2, r3, r4, times
from low_pass_filter import butter_lowpass_filter

SECOND = 100
# SECOND_T = 5


def boyusu_restlessness_func(sensor_data: list, motion_threshold):

    length = len(sensor_data) - SECOND
    check_max = []
    for i in range(0, length, SECOND):
        abs_list = np.absolute(sensor_data[i : i + SECOND])
        max_value = np.max(abs_list)
        check_max.append(max_value)

    check_max = np.array(check_max)
    sensor_data = np.array(sensor_data)

    level_threshold = max(0.015, motion_threshold * np.mean(check_max))
    motion_strength = np.zeros(len(sensor_data))
    # print(len(motion_strength))

    sensordatak = np.transpose(sensor_data)

    for i in range(0, length + 1, SECOND):
        this_level = np.max(np.absolute(sensordatak[i : i + SECOND]))
        if this_level > level_threshold:
            motion_strength[i : i + SECOND] = this_level
            sensordatak[i : i + SECOND] = -5

    return sensordatak, motion_strength


if __name__ == "__main__":
    # print(r2[:10])
    r1temp = np.append(np.flipud(r1[:1000]), np.array(r1))

    sensor_data_array = butter_lowpass_filter(r1temp)

    sensor_data_array = sensor_data_array[1000:]
    # # print(sensor_data_array)
    # # talk about advantages of running things in a db instead of using local memory.
    # # show the db funcs psql

    sensordatak, motion_strength = boyusu_restlessness_func(sensor_data_array, 1.5)

    # # print(len(motion_strength))
    for i in range(len(motion_strength)):
        print(i, motion_strength[i])
   
