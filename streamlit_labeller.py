import os

import pandas as pd
import streamlit as st

from src.config import DATA_DIR, SAMPLES_DIRECTORY, RESULTS_FILE_NAME, BATCH_SIZE_PER_PERSON, SAMPLES_NAME, \
    INFO_FILE_NAME

st.set_page_config(layout='wide')
st.title("Fuzzy Annotator!")

user_name = "Karo"

# set up
person_directory = os.path.join(DATA_DIR,
                                user_name)
if not os.path.exists(person_directory):
    st.write("That is not your user name!!!")
    st.stop()
st.write(f"You are {user_name}")

results_file = os.path.join(person_directory,
                            RESULTS_FILE_NAME)
info_file = os.path.join(person_directory,
                         INFO_FILE_NAME)
sample_directory = os.path.join(person_directory,
                                SAMPLES_NAME)

st.session_state.info_df = pd.read_csv(info_file,
                                       index_col=0)


def get_sample(sample_id,
               samples_directory):
    return pd.read_csv(os.path.join(samples_directory,
                                    f"{sample_id}.csv"),
                       index_col=0)


def save_label(label):
    row = st.session_state.info_df.iloc[[st.session_state.sample_number]].copy()
    row['label'] = label
    st.session_state.results_df = pd.concat([st.session_state.results_df, row])

    st.session_state.results_df.to_csv(results_file)
    st.session_state.sample_number += 1
    # st.experimental_rerun()


def get_chart():
    df = get_sample(st.session_state.sample_number,
                    sample_directory)

    col1, col2 = st.columns([5, 1])

    col1.subheader(f"BVP signal ({st.session_state.sample_number} sample)")
    col1.line_chart(df['bvp'])

    col2.subheader("Label")
    with col2:
        good_button = st.button('Good',
                                on_click=save_label,
                                args=("Good",),
                                key='good_button')
        medium_button = st.button('Medium',
                                  on_click=save_label,
                                  args=("Medium",),
                                  key='medium_button')
        poor_button = st.button('Poor',
                                on_click=save_label,
                                args=("Poor",),
                                key='poor_button')


def get_result_df(results_file):
    results_df = pd.DataFrame()

    if os.path.isfile(results_file):
        results_df = pd.read_csv(results_file,
                                 index_col=0)
        print(f"Got results_df of len {results_df.shape[0]}")

    if results_df.shape[0] > 0:
        sample_number = results_df.shape[0]
    else:
        sample_number = 0

    return sample_number, results_df


sample_number, results_df = get_result_df(results_file)

if 'sample_number' not in st.session_state:
    st.session_state.sample_number = sample_number

if 'results_df' not in st.session_state:
    st.session_state.results_df = results_df

st.progress(st.session_state.sample_number / BATCH_SIZE_PER_PERSON)

get_chart()

if st.session_state.sample_number >= BATCH_SIZE_PER_PERSON:
    st.text('THANK YOU, YOU ARE DONE!')
    st.balloons()
    st.stop()
