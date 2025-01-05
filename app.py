import streamlit as st
import sounddevice as sd
import soundfile as sf
from io import BytesIO
import time
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App configuration
st.set_page_config(page_title="Vent", layout="wide")

# Sidebar
st.sidebar.title("Vent")
st.sidebar.write("Record and playback your project explanations.")

# Main page
st.title("Vent")
st.write("Easily record yourself explaining your projects and play them back.")

# Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)


# Layout
col1, col2 = st.columns(2)

# Variables to manage state
if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = None

if "recording" not in st.session_state:
    st.session_state.recording = False

if "start_time" not in st.session_state:
    st.session_state.start_time = 0

if "stop_time" not in st.session_state:
    st.session_state.stop_time = 0

# Left column: Recording functionality
with col1:
    st.subheader("Record Your Explanation")
    
    # Get a list of available input devices
    device_list = [
        dev['name'] for dev in sd.query_devices() if dev['max_input_channels'] > 0
    ]
    selected_device = st.selectbox('Select Input Device', device_list)

    if st.session_state.recording:
        elapsed_time = time.time() - st.session_state.start_time
        st.write(f"Recording in progress... {elapsed_time:.2f} s")
    
    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("Start Recording"):
            st.session_state.recording = True
            st.session_state.start_time = time.time()
            st.session_state.stop_time = 0  # Reset stop time
            fs = 44100
            st.session_state.audio_data = sd.rec(
                int(600 * fs),  # Just an initial buffer, will adjust on stop
                samplerate=fs,
                channels=2,
                dtype='int16',
                device=device_list.index(selected_device)
            )
            st.write("Recording started...")

    with col_stop:
        if st.button("Stop Recording"):
            st.session_state.stop_time = time.time()
            sd.stop()
            sd.wait()
            fs = 44100
            duration = int((st.session_state.stop_time - st.session_state.start_time) * fs)
            st.session_state.audio_buffer = BytesIO()
            sf.write(st.session_state.audio_buffer, st.session_state.audio_data[:duration], fs, format='WAV')
            st.session_state.audio_buffer.seek(0)
            st.session_state.recording = False
            st.success("Recording completed.")

# Right column: Playback functionality
with col2:
    st.subheader("Playback Your Explanation")

    if st.session_state.audio_buffer is not None:
        st.audio(st.session_state.audio_buffer, format="audio/wav")
    else:
        st.write("No recording available to play back.")

    # Section for Transcription
    st.divider()
    st.write("Transcription of Your Explanation")
    
    # Save the audio buffer to a temporary file for transcription
    if st.session_state.audio_buffer is not None:
        temp_filename = "audio.wav"
        with open(temp_filename, "wb") as temp_file:
            temp_file.write(st.session_state.audio_buffer.read())

        # Transcription using Groq Whisper model
        try:
            with open(temp_filename, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(temp_filename, file.read()),
                    model="whisper-large-v3",
                    prompt="This recording is a snippet of a project explanation that will be used to write project documentation.",
                    response_format="verbose_json",
                )
            st.code(transcription.text, language='text')
            
            # Clear the audio buffer
            st.session_state.audio_buffer = None
            # Reset the temporary file pointer
            st.session_state.audio_buffer.seek(0)
            # Reset the recording state
            st.session_state.recording = False
            # Delete the temporary file
            try:
                os.remove(temp_filename)
            except OSError as e:
                st.error(f"Error: {e.strerror}")
        except Exception as e:
            st.write(f"Error transcribing audio: {e}")
        
        # Clean up temporary file
        os.remove(temp_filename)
