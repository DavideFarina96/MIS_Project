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

PLOT_SIZE = (13,7)

# How many points to create in the quantization of the pressure log
target_points = 1000

# FUNCTIONS #########################################################
# File names generation
user_data_raw = {}
user_data = {}


# Utility functions
def error_readFile(experiment, filename):
    f = open(filename, 'r')

    # Init dictionary for experiment keyword
    if (not experiment in user_data_raw):
        user_data_raw[experiment] = []

    # Read file and add values to the dictionaries
    for exp in f.readlines():
        val_raw = exp.split(" ")[1]
        val = float(val_raw[0:len(val_raw)-2])
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


def pressure_readFile(experiment, filename):
    f = open(filename, 'r')

    # Read the file
    lines = f.readlines()

    index = 0

    # Accocate the required space for the experiment keyword
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
        # remove ; from string and convert it to float
        val = float(val_raw[0:len(val_raw)-2])

        # Add value to the dataset
        user_data_raw[experiment][index] = [time, val]

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
        start_index = i*quantization_step
        end_index = start_index + quantization_step if i != target_points - \
            1 else len(user_data_raw[experiment])

        for j in range(start_index, end_index):
            time_sum += user_data_raw[experiment][j, 0]
            val_sum += user_data_raw[experiment][j, 1]

        # Convert elapsed time milliseconds to minutes
        elapsed_minutes = (
            (time_sum / (end_index - start_index)) - start_time) / 60000

        # Add the quantived point with avg time and val
        user_data[experiment][i] = [
            elapsed_minutes, val_sum / (end_index - start_index)]

    print("Completed", experiment)


def pressure_avg(experiment):
    # Allocate the required space
    user_data[experiment] = np.empty((target_points, 2))

    for i in range(target_points):
        _sum_time = 0
        _sum_val = 0

        for user in range(1, N_USERS+1):
            _sum_time += user_data[experiment + "_" + "u" + str(user)][i][0]
            _sum_val += user_data[experiment + "_" + "u" + str(user)][i][1]

        user_data[experiment][i] = [_sum_time / N_USERS, _sum_val / N_USERS]


# MAIN ################################################################
# Create the data structures for the measured error
measure = "error"

for feedback_type in FEEDBACK_TYPES:
    for user in range(1, N_USERS+1):
        for path_name in PATH_NAMES:
            for number in range(1, N_ATTEMPTS+1):
                error_readFile(experiment=measure + "_" + "u" + str(user) + "_" + feedback_type,
                               filename=logs_folder + "u" + str(user) + "/" + measure + "_" + path_name + "_" + feedback_type + "_" + str(number) + ".txt")
        # Compute average for a single user
        error_computeAvg(experiment=measure + "_" + "u" +
                         str(user) + "_" + feedback_type)

# Create the data structures for the measured pressure
measure = "pressure"

for user in range(1, N_USERS+1):
    for feedback_type in FEEDBACK_TYPES:
        for path_name in PATH_NAMES:
            for number in range(1, N_ATTEMPTS+1):
                pressure_readFile(experiment=measure + "_" + "u" + str(user),
                                  filename=logs_folder + "u" + str(user) + "/" + measure + "_" + path_name + "_" + feedback_type + "_" + str(number) + ".txt")
    pressure_sort_quantize(experiment=measure + "_" + "u" + str(user))

# Pressure for all users combined
pressure_avg(experiment="pressure")


# ERROR GRAPH ##############################################################
def computeDiffPercentage(_no_feedback, _measure):
    _diff = _measure - _no_feedback
    return (_diff / _no_feedback) * 100


LABELS = []
AUDIO = []
HAPTIC = []
BOTH = []

# User specific values
for user in range(1, N_USERS+1):
    LABELS.append("U" + str(user))
    _NO_FEEDBACK = user_data["error_u" + str(user) + "_NO_FEEDBACK"]
    AUDIO.append(computeDiffPercentage(_NO_FEEDBACK, user_data["error_u" +
                                                               str(user) + "_AUDIO"]))
    HAPTIC.append(computeDiffPercentage(_NO_FEEDBACK, user_data["error_u" +
                                                                str(user) + "_HAPTIC"]))
    BOTH.append(computeDiffPercentage(_NO_FEEDBACK, user_data["error_u" +
                                                              str(user) + "_BOTH"]))

# Average values
LABELS.append("AVG")
AUDIO.append(sum(AUDIO) / len(AUDIO))
HAPTIC.append(sum(HAPTIC) / len(HAPTIC))
BOTH.append(sum(BOTH) / len(BOTH))

x = np.arange(len(LABELS))  # the label locations
width = 0.2  # the width of the bars

fig, ax = plt.subplots(figsize=PLOT_SIZE)
rects1 = ax.bar(x - width, AUDIO, width, label='AUDIO')
rects2 = ax.bar(x, HAPTIC, width, label='HAPTIC')
rects3 = ax.bar(x + width, BOTH, width, label='BOTH')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Error in %')
ax.set_title('Average % error of users per feedback type')
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
# plt.show()
plt.savefig("Error.svg", format="svg")


# PRESSURE GRAPH ##############################################################
fig, ax = plt.subplots(figsize=PLOT_SIZE)
ax.set_title('Quantized value from the pressure sensor per user')
ax.set_ylabel('Pressure sensor')
ax.set_xlabel('Elapsed minutes')

# Plot user specific data
for user in range(1, N_USERS+1):
    plt.plot(user_data["pressure_u" + str(user)][:, 0],
             user_data["pressure_u" + str(user)][:, 1], label='U' + str(user))
# Plot average of values
plt.plot(user_data["pressure"][:, 0],
         user_data["pressure"][:, 1], label='AVG')

plt.legend()
fig.tight_layout()
# plt.show()
plt.savefig("Pressure.svg", format="svg")