import os
from datetime import timedelta, datetime

import pandas as pd
from tqdm import tqdm

from .config import DATA_DIR, SESSIONS_DIR, BVP_FILE_NAME, TIME_SPAN_SAMPLE, POSSIBLE_SAMPLES_FILE_PATH, \
    NUMBER_OF_PEOPLE, PEOPLE, BATCH_SIZE_PER_PERSON, USED_SAMPLES_FILE_NAME, BATCH_COLUMNS, \
    DATA_FORMAT, SAMPLES_DIRECTORY, SAMPLES_NAME, INFO_FILE_NAME


def check_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def create_batches(possible_samples_df,
                   batch_size=BATCH_SIZE_PER_PERSON,
                   number_of_people=NUMBER_OF_PEOPLE
                   ):
    time_span_directory = os.path.join(DATA_DIR,
                                       SAMPLES_DIRECTORY)
    check_directory(directory=time_span_directory)
    date_directory = os.path.join(time_span_directory,
                                  datetime.now().strftime(DATA_FORMAT))
    check_directory(directory=date_directory)

    batches = dict()
    # exclude used samples
    possible_samples_df = exclude_used_samples(possible_samples_df,
                                               directory=date_directory)

    for person_number in range(number_of_people):
        batch_samples, possible_samples_df = create_batch(possible_samples_df,
                                                          batch_size)
        batch_samples.reset_index(drop=True,
                                  inplace=True)
        batches[person_number] = batch_samples

    save_batches(batches=batches,
                 directory=date_directory)


def save_batches(batches,
                 directory):
    used_samples = pd.DataFrame(columns=BATCH_COLUMNS)

    for person_number, batch in tqdm(batches.items(),
                                              desc="People",
                                              position=0,
                                              leave=False,
                                              colour='green'):
        person_directory = os.path.join(directory,
                                        PEOPLE[person_number])
        check_directory(directory=person_directory)

        # save to folder of person number
        # save info
        batch_file_path = os.path.join(person_directory,
                                       INFO_FILE_NAME)
        batch.to_csv(batch_file_path)
        used_samples = pd.concat([used_samples, batch])

        # save actual data
        samples_directory = os.path.join(person_directory, SAMPLES_NAME)
        check_directory(samples_directory)
        save_batch_data(samples_directory,
                        batch)

    # save to json file? csv file? used rows
    used_samples.to_csv(os.path.join(directory,
                                     USED_SAMPLES_FILE_NAME),
                        index=False)


def save_batch_data(directory,
                    batch_info):
    for index, row in tqdm(batch_info.iterrows(),
                           desc="Saving batches data",
                           position=2,
                           leave=False,
                           colour='blue'):
        start = row[BATCH_COLUMNS[2]]
        end = row[BATCH_COLUMNS[3]]

        path_file = os.path.join(DATA_DIR,
                                 str(row[BATCH_COLUMNS[0]]),
                                 SESSIONS_DIR,
                                 str(row[BATCH_COLUMNS[1]]),
                                 BVP_FILE_NAME)
        df = get_bvp_data_frame(path_file)
        batch_df = df[(df['time'] >= start) & (df['time'] < end)]
        batch_df.reset_index(drop=True,
                             inplace=True)
        batch_df.to_csv(os.path.join(directory,
                                     f"{index}.csv"))


def get_used_samples(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None


def exclude_used_samples(possible_samples_df,
                         directory):
    used_df = get_used_samples(file_path=os.path.join(directory,
                                                      USED_SAMPLES_FILE_NAME))
    return exclude_data_frames(possible_samples_df,
                               used_df) if used_df is not None else possible_samples_df


def exclude_data_frames(df1,
                        df2):
    return pd.merge(df1,
                    df2,
                    indicator=True,
                    how='outer').query('_merge=="left_only"').drop('_merge',
                                                                   axis=1)


def create_batch(possible_samples_df,
                 batch_size):
    batch_samples = possible_samples_df.sample(n=batch_size)
    new_possible_samples_df = exclude_data_frames(possible_samples_df,
                                                  batch_samples)

    return batch_samples, new_possible_samples_df


def get_possible_samples():
    if os.path.exists(POSSIBLE_SAMPLES_FILE_PATH):
        df = get_possible_samples_from_file()
        if not df.empty:
            return df

    possible_samples = []
    for patient_id in tqdm(os.listdir(DATA_DIR),
                           desc="Getting data",
                           position=0,
                           leave=False,
                           colour='green'):
        if patient_id.startswith("p"):
            patient_path = os.path.join(DATA_DIR,
                                        patient_id,
                                        SESSIONS_DIR)

            for session_id in tqdm(os.listdir(patient_path),
                                   position=1,
                                   leave=False,
                                   colour='red',
                                   desc=f'Patient {patient_id}'):
                file_path = os.path.join(patient_path,
                                         session_id,
                                         BVP_FILE_NAME)
                if not os.path.exists(file_path):
                    continue

                df = get_bvp_data_frame(file_path=file_path)

                start = df['time'].min()
                end = df['time'].max()
                diff = (end - start).total_seconds()

                number_of_samples = int(diff // TIME_SPAN_SAMPLE)

                for _ in range(number_of_samples):
                    end = start + timedelta(seconds=TIME_SPAN_SAMPLE)
                    possible_samples.append((patient_id, session_id, start, end))
                    start = end

    possible_samples_df = pd.DataFrame(possible_samples,
                                       columns=BATCH_COLUMNS)
    save_possible_samples(possible_samples_df)
    return possible_samples_df


def get_bvp_data_frame(file_path):
    df = pd.read_csv(file_path,
                     header=None)
    df['time'] = pd.to_datetime(df[0],
                                unit='s',
                                origin='unix')

    df = df.sort_values('time')
    df = df.rename(columns={1: "bvp"})
    df = df.dropna()

    df = df[['time', 'bvp']]
    return df


def save_possible_samples(possible_samples_df,
                          file_path=POSSIBLE_SAMPLES_FILE_PATH):
    possible_samples_df.to_csv(file_path,
                               index=False)


def get_possible_samples_from_file(file_path=POSSIBLE_SAMPLES_FILE_PATH):
    possible_samples_df = pd.read_csv(file_path)
    return possible_samples_df
