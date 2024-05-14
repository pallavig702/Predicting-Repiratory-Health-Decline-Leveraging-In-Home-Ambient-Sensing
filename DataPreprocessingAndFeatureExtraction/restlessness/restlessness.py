from low_pass_filter import butter_lowpass_filter
from boyusu_restlessness_new_sub_function import boyusu_restlessness_func
import numpy as np
import db_funcs as db
from pprint import pprint
import pandas as pd

MINUTE = 5_000


def determine_restlessness(r1: list, r2: list, r3: list, r4: list, start_times: list):
    """
    Parameters
    ----------
    :param r1: list
    :param r2: list
    :param r3: list
    :param r4: list
    :param filename: str

    Returns
    -------
    :return: output_final, motion_strength_final, motion_summary
    """

    if len(r1) < MINUTE or len(r2) < MINUTE or len(r3) < MINUTE or len(r4) < MINUTE:
        print("Not enough data")
        return [], [], []
    #print(start_times)
    
    r1temp = np.append(np.flipud(r1[:1000]), np.array(r1))
    r2temp = np.append(np.flipud(r2[:1000]), np.array(r2))
    r3temp = np.append(np.flipud(r3[:1000]), np.array(r3))
    r4temp = np.append(np.flipud(r4[:1000]), np.array(r4))

    sensordatar1 = butter_lowpass_filter(r1temp)
    sensordatar2 = butter_lowpass_filter(r2temp)
    sensordatar3 = butter_lowpass_filter(r3temp)
    sensordatar4 = butter_lowpass_filter(r4temp)

    sensordatar1 = sensordatar1[1000:]
    sensordatar2 = sensordatar2[1000:]
    sensordatar3 = sensordatar3[1000:]
    sensordatar4 = sensordatar4[1000:]

    sensor_data_array = [sensordatar1, sensordatar2, sensordatar3, sensordatar4]
    #sensor_data_array = [r1, r2, r3, r4]
    motion_threshold = 1.5

    output_array, motion_strength_array = [], []

    for sensor_data in sensor_data_array:
        output, motion_strength = boyusu_restlessness_func(
            sensor_data, motion_threshold
        )
        output_array.append(output)
        motion_strength_array.append(motion_strength)

    output_array = np.array(output_array)

    for output in output_array:
        # output[output > -4] = 0
        output[output == -5] = 2
        output[output != 2] = 0

    output_final = np.maximum(output_array[0], output_array[1])
    output_final = np.maximum(output_final, output_array[2])
    output_final = np.maximum(output_final, output_array[3])

    zeros_array = np.zeros(len(r1) - len(output_array[0]))
    output_final = np.append(output_final, zeros_array)

    motion_strength_final = np.maximum(
        motion_strength_array[0], motion_strength_array[1]
    )
    motion_strength_final = np.maximum(motion_strength_final, motion_strength_array[2])
    motion_strength_final = np.maximum(motion_strength_final, motion_strength_array[3])

    motion_dict = {}
    starts, ends, z = 0, 0, 0

    try:
        for i in range(1, len(output_final)):
            if output_final[i] - output_final[i - 1] == 2:
                motion_dict[z] = {
                    "start_motion": start_times[i],
                    "start_index": i,
                }
                starts += 1
            elif output_final[i] - output_final[i - 1] == -2:
                if z not in motion_dict:
                    motion_dict[z] = {}
                motion_dict[z]["end_motion"] = start_times[i]
                motion_dict[z]["end_index"] = i
                ends += 1
                z += 1
        if starts > ends:
            motion_dict[z]["end_motion"] = start_times[i]
            motion_dict[z]["end_index"] = i
        elif ends > starts:
            motion_dict[0]["start_motion"] = start_times[0]
            motion_dict[0]["start_index"] = 0
    except KeyError:
        print(
            f"There's a KeyError in block starting at {start_times[0]} and ending at {start_times[-1]}"
        )
        print(motion_dict)
        quit()

    motion_strength_level_temp = []
    motion_duration_in_second = []

    array_size = max(starts, ends)

    for i in range(array_size):
        # print(i)

        try:
            start_motion_index = motion_dict[i]["start_index"]
            end_motion_index = motion_dict[i]["end_index"]
            level_temp = np.max(
                motion_strength_final[start_motion_index:end_motion_index]
            )
            motion_strength_level_temp.append(level_temp)
            motion_duration = (
                motion_dict[i]["end_motion"] - motion_dict[i]["start_motion"]
            ).total_seconds()
            motion_duration_in_second.append(motion_duration)
        except KeyError:
            print(
                f"There's a KeyError in block starting at {start_times[0]} and ending at {start_times[-1]}"
            )
            print(motion_dict)
            quit()
            # print(start_times)

    motion_duration_in_second = np.array(motion_duration_in_second)
    motion_strength_level_temp = np.array(motion_strength_level_temp)

    motion_duration_in_second[motion_duration_in_second < 1] = 1

    motion_strength_level = motion_strength_level_temp

    motion_strength_level[motion_strength_level_temp < 0.15] = 1
    motion_strength_level[motion_strength_level_temp > 0.15] = 2
    motion_strength_level[motion_strength_level_temp > 0.3] = 3

    # generate the motion summary
    motion_summary = {
        "starts_motion": [],
        "ends_motion": [],
        "motion_duration_in_second": [],
        "motion_strength_level": [],
    }

    for i in range(array_size):
        motion_summary["starts_motion"].append(motion_dict[i]["start_motion"])
        motion_summary["ends_motion"].append(motion_dict[i]["end_motion"])
        motion_summary["motion_duration_in_second"].append(motion_duration_in_second[i])
        motion_summary["motion_strength_level"].append(motion_strength_level[i])
    df = pd.DataFrame.from_dict(motion_summary)
    return(df)
    #return output_final, motion_strength_final, motion_summary


if __name__ == "__main__":

    use_db = False

    if not use_db:
        from static.bed_data import r1, r2, r3, r4, times
        '''
        output_final, motion_strength_final, motion_summary = determine_restlessness(
            r1, r2, r3, r4, times
        )

        #pprint(motion_summary)
        '''
        DF = determine_restlessness(r1, r2, r3, r4, times)
        #print(times)
        print(DF.tail())
        print(DF.groupby('motion_strength_level')['motion_strength_level'].sum())
        quit()

    df = db.get_data_for_restlessness(
        "bed_raw_3054_only", "2018-08-28 21:30:00.0", "2018-08-29 22:00:00.00"
    )

    for index, row in df.iterrows():

        params = db.format_data_for_restlessness(row)

        output_final, motion_strength_final, motion_summary = determine_restlessness(
            **params
        )

        print(f"start {params['start_times'][0]} end {params['start_times'][-1]}")
        output_final, motion_strength_final, motion_summary = determine_restlessness(
            **params
        )
        pprint(motion_summary)
