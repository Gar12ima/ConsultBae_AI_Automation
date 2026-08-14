# TASK 3 - Audio Collection App Documentation

## Project Title
ConsultBae Audio Collection App

---

## Objective

The objective of this task was to develop an audio collection application where users can upload audio files along with their personal details. The application processes uploaded audio files, extracts important audio features, and stores all information in a structured SQLite database.

---

## Technologies Used

- Python
- Streamlit
- SQLite Database
- Librosa
- SoundFile
- NumPy

---

## Application Features

### 1. Audio Upload System

Implemented a Streamlit-based user interface that allows users to:

- Enter Name
- Enter Phone Number
- Upload audio files (.mp3/.wav)
- Preview uploaded audio
- Submit audio data


---

### 2. Audio Processing and Analysis

The application performs audio analysis using Librosa and SoundFile libraries.

Extracted audio parameters:

- Audio Duration
- Sample Rate
- Bitrate / Audio Subtype
- Loudness Level (dB)


---

### 3. Database Storage

Created SQLite database:
