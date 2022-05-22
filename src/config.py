import os

DATA_DIR = os.path.join(os.getcwd(), "data")
SESSIONS_DIR = "sessions"
BVP_FILE_NAME = "bvp.csv"

DATA_FORMAT = "%d%m%Y%H%M"

# in seconds
TIME_SPAN_SAMPLE = 10

POSSIBLE_SAMPLES_FILE_NAME = "possible_samples.csv" #TODO: add number of time span to name
POSSIBLE_SAMPLES_FILE_PATH = os.path.join(DATA_DIR, POSSIBLE_SAMPLES_FILE_NAME)

SAMPLES_DIRECTORY = str(TIME_SPAN_SAMPLE) + "_seconds_samples"

NUMBER_OF_PEOPLE = 3
PEOPLE = {
    0: "Karo",
    1: "Janek",
    2: "Tomek",
    3: "Random"
}

BATCH_SIZE_PER_PERSON = 350
# TOTAL_BATCHES = 1100

BATCH_COLUMNS = ['patient id', 'session', 'start', 'end']

USED_SAMPLES_FILE_NAME = "used_samples.csv"
USED_SAMPLES_FILE_PATH = os.path.join(DATA_DIR, USED_SAMPLES_FILE_NAME)

SAMPLES_NAME = "samples"
INFO_FILE_NAME = "info.csv"
RESULTS_FILE_NAME = "results.csv"
