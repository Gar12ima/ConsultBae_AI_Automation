import streamlit as st
import os
import librosa
import soundfile as sf
import sqlite3
import numpy as np


# -------------------------------
# Page Config
# -------------------------------

st.set_page_config(
    page_title="ConsultBae Audio Collection App",
    layout="centered"
)


st.title("ConsultBae Audio Collection App")



# -------------------------------
# Folder Setup
# -------------------------------

AUDIO_FOLDER = "audio_files"

if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)



# -------------------------------
# Database Setup
# -------------------------------

conn = sqlite3.connect(
    "audio_database.db",
    check_same_thread=False
)

cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS audio_records(

id INTEGER PRIMARY KEY AUTOINCREMENT,

name TEXT,

phone TEXT,

file_path TEXT,

duration REAL,

sample_rate INTEGER,

bitrate TEXT,

loudness REAL

)
""")


conn.commit()



# -------------------------------
# Sidebar
# -------------------------------

page = st.sidebar.selectbox(
    "Select Page",
    [
        "Upload Audio",
        "View Submissions"
    ]
)




# =====================================================
# PAGE 1 : UPLOAD AUDIO
# =====================================================


if page == "Upload Audio":


    st.header("Upload Audio")


    name = st.text_input(
        "Enter Name"
    )


    phone = st.text_input(
        "Enter Phone Number"
    )


    audio_file = st.file_uploader(
        "Upload Audio File",
        type=["wav","mp3"]
    )



    if audio_file:


        st.audio(audio_file)



        if st.button("Submit Audio"):


            file_path = os.path.join(
                AUDIO_FOLDER,
                audio_file.name
            )


            with open(file_path,"wb") as f:

                f.write(
                    audio_file.getbuffer()
                )



            # --------------------
            # Audio Analysis
            # --------------------


            y, sr = librosa.load(
                file_path
            )


            duration = librosa.get_duration(
                y=y,
                sr=sr
            )



            rms = librosa.feature.rms(
                y=y
            ).mean()



            loudness_db = float(
                20 * np.log10(
                    rms + 1e-6
                )
            )



            audio_info = sf.info(
                file_path
            )


            bitrate = str(
                audio_info.subtype
            )



            # --------------------
            # Save Database
            # --------------------


            cursor.execute(
            """
            INSERT INTO audio_records
            (
            name,
            phone,
            file_path,
            duration,
            sample_rate,
            bitrate,
            loudness
            )

            VALUES(?,?,?,?,?,?,?)

            """,

            (
            name,
            phone,
            file_path,
            duration,
            sr,
            bitrate,
            loudness_db
            )

            )


            conn.commit()



            st.success(
                "Audio saved successfully!"
            )


            st.write(
                "Duration:",
                round(duration,2),
                "seconds"
            )


            st.write(
                "Sample Rate:",
                sr,
                "Hz"
            )


            st.write(
                "Bitrate:",
                bitrate
            )


            st.write(
                "Loudness:",
                round(loudness_db,2),
                "dB"
            )





# =====================================================
# PAGE 2 : VIEW SUBMISSIONS
# =====================================================


elif page == "View Submissions":


    st.header(
        "Audio Submissions"
    )


    cursor.execute(
    """
    SELECT
    name,
    phone,
    file_path,
    duration,
    sample_rate,
    bitrate,
    loudness

    FROM audio_records

    """
    )


    records = cursor.fetchall()



    if len(records)==0:


        st.warning(
            "No submissions found"
        )


    else:


        for record in records:



            name = record[0]
            phone = record[1]
            file_path = record[2]
            duration = record[3]
            sample_rate = record[4]
            bitrate = record[5]
            loudness = record[6]



            # Fix old database values

            try:

                if isinstance(loudness, bytes):

                    loudness = float(
                        int.from_bytes(
                            loudness,
                            byteorder="little"
                        )
                    )

                else:

                    loudness = float(loudness)


            except:

                loudness = 0.0





            st.subheader(
                name
            )


            st.write(
                "Phone:",
                phone
            )



            if os.path.exists(file_path):

                st.audio(
                    file_path
                )



            st.write(
                "Duration:",
                round(duration,2),
                "seconds"
            )


            st.write(
                "Sample Rate:",
                sample_rate,
                "Hz"
            )


            st.write(
                "Bitrate:",
                bitrate
            )


            st.write(
                "Loudness:",
                round(loudness,2),
                "dB"
            )


            st.divider()