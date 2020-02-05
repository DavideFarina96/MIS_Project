import numpy as np
import tkinter
import matplotlib.pyplot as plt
import pandas as pd

# VARIABLES ##########################################################
N_USERS = 10
PATH_NAMES = ["path1", "path2", "path3"]
FEEDBACK_TYPES = ["NO_FEEDBACK", "AUDIO", "HAPTIC", "BOTH"]
N_ATTEMPTS = 3
logs_folder = "logs/"

# How many points to create in the quantization of the pressure log
target_points = 10000

# FUNCTIONS #########################################################
# File names generation
user_data_raw = {}
user_data = {}


# Utility functions
def error_readFile(experiment_all, experiment, filename):
    f = open(filename, 'r')

    # Init dictionary for experiment keyword
    if (not experiment_all in user_data_raw):
        user_data_raw[experiment_all] = []
    if (not experiment in user_data_raw):
        user_data_raw[experiment] = []

    # Read file and add values to the dictionaries
    for exp in f.readlines():
        val_raw = exp.split(" ")[1]
        val = float(val_raw[0:len(val_raw)-2])
        user_data_raw[experiment_all].append(val)
        user_data_raw[experiment].append(val)

    f.close()


def error_computeAvg(experiment):
    # Init dictionary for experiment keyword
    if (not experiment in user_data):
        user_data[experiment] = []

    # Compute the avg of the raw data and insert it in the dict
    user_data[experiment] = sum(
        user_data_raw[experiment]) / float(len(user_data_raw[experiment]))

    # DEBUG print the result
    print(experiment + " " + str(user_data[experiment]))


def getMillisec(time_raw):
    # Compute milliseconds
    time_raw = list(map(float, time_raw.split(":")))
    return time_raw[0] * 3600000 + time_raw[1] * 60000 + time_raw[2] * 1000 + time_raw[3]


def pressure_readFile(experiment_all, experiment, filename):
    f = open(filename, 'r')

    # Read the file
    lines = f.readlines()

    # index_all=0
    index = 0

    # Init dictionary for experiment keyword
    # if (not experiment_all in user_data_raw):
    #     user_data_raw[experiment_all]=np.empty((len(lines), 2))
    # else:
    #     index_all=len(user_data_raw[experiment_all])
    #     user_data_raw[experiment_all]=np.append(
    #         user_data_raw[experiment_all], np.empty((len(lines), 2)), axis=0)

    if (not experiment in user_data_raw):
        user_data_raw[experiment] = np.empty((len(lines), 2))
    else:
        index = len(user_data_raw[experiment])
        user_data_raw[experiment] = np.append(
            user_data_raw[experiment], np.empty((len(lines), 2)), axis=0)

    # Read file and add values to the dictionaries
    for exp in lines:
        time_raw, val_raw = exp.split(" ")

        time = getMillisec(time_raw)
        val = float(val_raw[0:len(val_raw)-2])

        # user_data_raw[experiment_all][index_all]=[val, val]
        user_data_raw[experiment][index] = [time, val]

        # index_all += 1
        index += 1

    f.close()


def pressure_sort_quantize(experiment):
    # Sort values by time
    user_data_raw[experiment] = user_data_raw[experiment][user_data_raw[experiment][:, 0].argsort()]

    # Compute the number of raw points to compute the qunatized point
    quantization_step = int(len(user_data_raw[experiment]) / target_points)

    # Allocate the required space
    user_data[experiment] = np.empty((target_points, 2))

    # Get the starting time of the experiment
    start_time = user_data_raw[experiment][0, 0]

    for i in range(target_points):
        time_sum = 0
        val_sum = 0
        for j in range(i*quantization_step, (i+1)*quantization_step):
            time_sum += user_data_raw[experiment][j, 0]
            val_sum += user_data_raw[experiment][j, 1]

        # Convert elapsed time milliseconds to minutes
        elapsed_minutes = ((time_sum / quantization_step) - start_time) / 60000
        
        # Add the quantived point with avg time and val
        user_data[experiment][i] = [elapsed_minutes, val_sum / quantization_step]

        # TODO some points are left behind

    print("Completed", experiment)


# MAIN ################################################################
# Create the data structures for the measured error
measure = "error"

for feedback_type in FEEDBACK_TYPES:
    for user in range(1, N_USERS+1):
        for path_name in PATH_NAMES:
            for number in range(1, N_ATTEMPTS+1):
                error_readFile(experiment_all=measure + "_" + feedback_type,
                               experiment=measure + "_" + "u" +
                               str(user) + "_" + feedback_type,
                               filename=logs_folder + "u" + str(user) + "/" + measure + "_" + path_name + "_" + feedback_type + "_" + str(number) + ".txt")
        # Compute average for a single user
        error_computeAvg(experiment=measure + "_" + "u" +
                         str(user) + "_" + feedback_type)
    # Compute average for all users
    error_computeAvg(experiment=measure + "_" + feedback_type)

# Create the data structures for the measured pressure
measure = "pressure"

for user in range(1, N_USERS+1):
    for feedback_type in FEEDBACK_TYPES:
        for path_name in PATH_NAMES:
            for number in range(1, N_ATTEMPTS+1):
                pressure_readFile(experiment_all=measure,
                                  experiment=measure + "_" + "u" + str(user),
                                  filename=logs_folder + "u" + str(user) + "/" + measure + "_" + path_name + "_" + feedback_type + "_" + str(number) + ".txt")
    pressure_sort_quantize(experiment=measure + "_" + "u" + str(user))

# TODO pressure for all users combined


# ERROR GRAPH ##############################################################
LABELS = []
AUDIO = []
HAPTIC = []
BOTH = []

# User specific values
for user in range(1, N_USERS+1):
    LABELS.append("U" + str(user))
    _no_feedback = user_data["error_u" + str(user) + "_NO_FEEDBACK"]
    AUDIO.append(user_data["error_u" +
                           str(user) + "_AUDIO"] - _no_feedback)
    HAPTIC.append(user_data["error_u" +
                            str(user) + "_HAPTIC"] - _no_feedback)
    BOTH.append(user_data["error_u" + str(user) + "_BOTH"] - _no_feedback)

# Average values
LABELS.append("AVG")
_no_feedback = user_data["error_NO_FEEDBACK"]
AUDIO.append(user_data["error_AUDIO"] - _no_feedback)
HAPTIC.append(user_data["error_HAPTIC"] - _no_feedback)
BOTH.append(user_data["error_BOTH"] - _no_feedback)

x = np.arange(len(LABELS))  # the label locations
width = 0.2  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width, AUDIO, width, label='AUDIO')
rects2 = ax.bar(x, HAPTIC, width, label='HAPTIC')
rects3 = ax.bar(x + width, BOTH, width, label='BOTH')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Error')
ax.set_title('Average error of users per feedback type')
ax.set_xticks(x)
ax.set_xticklabels(LABELS)
ax.legend()


def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{0:.1f}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


autolabel(rects1)
autolabel(rects2)
autolabel(rects3)
fig.tight_layout()
plt.show()


# PRESSURE GRAPH ##############################################################
fig, ax = plt.subplots()
ax.set_title('Quantized value from the pressure sensor per user')
ax.set_ylabel('Pressure sensor')
ax.set_xlabel('Elapsed minutes')
ax.legend()

for user in range(1, N_USERS+1):
    plt.plot(user_data["pressure_u" + str(user)][:, 0], user_data["pressure_u" + str(user)][:, 1], label='U' + str(user))
fig.tight_layout()
plt.legend()
plt.show()
